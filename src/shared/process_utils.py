from multiprocessing import Process, Queue
from queue  import Empty
from time import sleep
from typing import Callable, Tuple

from lch.core.class_container import ClassContainer

class Wrapper:
    def __init__(
        self, 
        function: Callable, 
        consumer_queue: Queue, 
        deposit_queue: Queue
    ):
        self._function = function
        self._consumer_queue = consumer_queue
        self._deposit_queue = deposit_queue
    
    def run(self):
        should_keep_on_consuming = True
        retries_count = 0
        while should_keep_on_consuming:
            try:
                if retries_count == 10:
                    should_keep_on_consuming = False
                data = self._consumer_queue.get_nowait()
                result = self._function(data)
                if self._deposit_queue:
                    self._deposit_queue.put_nowait(result)
            except Empty:
                sleep(3)
                retries_count += 1

def clone_queue_service_wrapper(row_data: Tuple[str, str]):
    clone_service = ClassContainer().get_clone_service()
    repo_id, repo_url = row_data[0], row_data[1]
    return clone_service.clone_repository(
        url=f'{repo_url}.git',
        repo_name=repo_id
    )

def ck_queue_service_wrapper(repository_dir: str):
    code_analysis_service = ClassContainer().get_code_analysis_service()
    code_analysis_service.analyse_project(repository_dir)

def create_listener_process(
    function: Callable, 
    consumer_queue: Queue,
    deposit_queue: Queue = None
):

    process = Process(
        target=Wrapper(function, consumer_queue, deposit_queue).run,
        daemon=True
    )
    return process

def maintain_process_alive_while_process_are_running(ps: list[Process]):
    all_process_are_dead = False
    while not all_process_are_dead:
        qtd_of_process_dead = 0
        for p in ps:
            if not p.is_alive():
                qtd_of_process_dead += 1
        all_process_are_dead = qtd_of_process_dead == 5

def create_queue():
    return Queue()