import asyncio
from typing import Coroutine

def create_async_task(function: Coroutine, *args, **kwargs):
    return asyncio.create_task(function(*args, **kwargs))

def run_tasks(tasks: list[asyncio.Task], concurrency_limit: int = None):
    if concurrency_limit:
        semaphore = asyncio.Semaphore(concurrency_limit)
        def coroutine_wrapper(task):
            with semaphore:
                return task()
        tasks = [coroutine_wrapper(task) for task in tasks]
    return asyncio.gather(*tasks)
        