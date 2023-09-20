from enum import Enum, auto
from multiprocessing import Process, Queue
from queue import Empty
from time import time
from typing import Any, Callable, TypeVar

class ExecutionType(Enum):
    CONSUMER = auto()
    PRODUCER = auto()
    CONSUMER_PRODUCER = auto()

_MaxExecutionTimeInSeconds = TypeVar('_MaxExecutionTimeInSeconds', bound=int)
_QueueName = TypeVar('_QueueName', bound=str)

class BackgroundMessagersProcessPool:

    class _FunctionWrapper:
        def consumer_wrapper(
            self, 
            function: Callable, 
            consumer_queue: Queue, 
            timeout: int
        ):
            keep_on_running = True
            while keep_on_running:
                try:
                    st = time()
                    value = consumer_queue.get(timeout=timeout+5)
                    function(value)
                except Empty:
                    ...
                finally:
                    end = round(time() - st)
                    keep_on_running = end < timeout

        def producer_wrapper(
            self,
            function: Callable,
            producer_queue: Queue,
            timeout: int
        ):
            keep_on_running = True
            while keep_on_running:  
                st = time()
                result = function()
                producer_queue.put(result)
                end = round(time() - st)
                keep_on_running = end < timeout

        def consumer_and_producer_wrapper(
            self, 
            function: Callable,
            consumer_queue: Queue,
            producer_queue: Queue,
            timeout: int
        ):
            keep_on_running = True
            while keep_on_running:
                st = time()
                try:
                    value = consumer_queue.get(timeout=timeout+5)
                    result = function(value)
                    if result:
                        producer_queue.put(result)
                except Empty:
                    ...
                finally:
                    end = round(time() - st)
                    keep_on_running = end < timeout

    def __init__(self, max_number_of_process: int):
        self._processes: list[Process] = []
        self._queues: dict[_QueueName, Queue] = {}
        self._number_of_running_processes = 0
        self.max_number_of_process = max_number_of_process

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if not exc_type and not exc_value and not exc_tb:
            self.await_execution()
    
    def await_execution(self):
        while self._number_of_running_processes != 0:
            number_of_alive_processes = 0
            for process in self._processes:
                if process.is_alive():
                    number_of_alive_processes += 1
            self._number_of_running_processes = number_of_alive_processes
    
    def start_process(
        self, 
        function: Callable,
        execution_type: ExecutionType,
        timeout: _MaxExecutionTimeInSeconds = 420,
        consumer_queue_name: _QueueName = None,
        producer_queue_name: _QueueName = None,
    ):
        if self._number_of_running_processes < self.max_number_of_process:
            function_wrapper = self._FunctionWrapper()
            consumer_queue = self._queues.get(consumer_queue_name)
            producer_queue = self._queues.get(producer_queue_name)
            if execution_type == ExecutionType.CONSUMER:
                process = Process(
                    target=function_wrapper.consumer_wrapper,
                    daemon=True,
                    kwargs={
                        'function': function,
                        'consumer_queue': consumer_queue,
                        'timeout': timeout
                    }
                )
            elif execution_type == ExecutionType.PRODUCER:
                process = Process(
                    target=function_wrapper.producer_wrapper,
                    daemon=True,
                    kwargs={
                        'function': function,
                        'producer_queue': consumer_queue,
                        'timeout': timeout
                    }
                )
            elif execution_type == ExecutionType.CONSUMER_PRODUCER:
                process = Process(
                    target=function_wrapper.consumer_and_producer_wrapper,
                    daemon=True,
                    kwargs={
                        'function': function,
                        'consumer_queue': consumer_queue,
                        'producer_queue': producer_queue,
                        'timeout': timeout
                    }
                )
            else:
                raise NotImplementedError(f'Execution type of {execution_type} is not yet implemeted')
            self._processes.append(process)
            process.start()
            self._number_of_running_processes += 1

    def define_queue(self, name: str):
        if not self._queues.get(name):
            self._queues[name] = Queue()
        else:
            raise ValueError(f'Queue with name {name} already exists')
    
    def publish_to_queue(self, name: str, values: list[Any]):
        queue = self._queues.get(name)
        if queue:
            for value in values:
                queue.put(value)