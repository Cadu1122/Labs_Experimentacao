
from lch.core.class_container import ClassContainer
from lch.shared.async_utils import run_async_function


@run_async_function
async def start():
    class_container = ClassContainer()
    analyser_service = class_container.get_analyzer_service()
    await analyser_service.lab_02()

start()