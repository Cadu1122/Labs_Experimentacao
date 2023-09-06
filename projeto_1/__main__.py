from projeto_1.core.class_container import ClassContainer
from projeto_1.core.file_persitance import ensure_all_necessary_paths_exist
from projeto_1.shared.async_utils import run_async_function

ensure_all_necessary_paths_exist()

@run_async_function
async def start():
    class_container = ClassContainer()
    analyzer_servcice = class_container.get_analyzer_service()
    await analyzer_servcice.analyse_most_famous_repositories()

start()