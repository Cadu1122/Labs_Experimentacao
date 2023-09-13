import asyncio
from asyncio import Future, Task


def create_async_task(fn: callable, *fn_args, **fn_kwargs):
    return asyncio.create_task(fn(*fn_args, **fn_kwargs))


async def get_async_results(functions: list[Task | Future], limit_to_x_tasks: int = None):
    if limit_to_x_tasks:
        semaphore = asyncio.Semaphore(limit_to_x_tasks)
        async def semaphored_tasks(task):
            async with semaphore:
                return await task
        functions = (semaphored_tasks(task) for task in functions)
    return await asyncio.gather(*functions)

def create_future(function: callable, *function_args):
    return asyncio.ensure_future(function(*function_args))

def run_async_function(function):
    def wrapper(*args, **kwargs):
        asyncio.run(function(*args, **kwargs))
    return wrapper

