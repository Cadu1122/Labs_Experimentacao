from pathlib import Path
from pandas import DataFrame
from typing import Any

from lch.core.config.constants import GRAPHIC_PATH


class GraphicService:
    def create_box_plot(
        self, 
        data: list[Any], 
        columns: list[str],
        file_path: Path
    ):
        data_frame = DataFrame(data, columns=columns)
        graphic = data_frame.boxplot(column=columns)
        graphic.get_figure().savefig(f'{file_path.as_posix()}')
        graphic.clear()
    
    def create_scatter_plot(
        self,
        data: list[Any, Any],
        columns: list[str],
        file_path: Path
    ):
        data_frame = DataFrame(data, columns=columns)
        data_frame.sort_values(by=columns, ascending=True, inplace=True)
        graphic = data_frame.plot.scatter(x=columns[0], y=columns[1], figsize=(10,5))
        graphic.get_figure().savefig(f'{file_path.as_posix()}')
        graphic.clear()
    
    def create_bar_plot(
        self,
        data: list[list[str], list[Any]],
        columns: list[str],
        file_path: Path
    ):
        data_frame = DataFrame({columns[0]: data[0], columns[1]: data[1]})
        graphic = data_frame.plot.bar(x=columns[0], y=columns[1], rot=45, figsize=(10,5))
        graphic.get_figure().savefig(f'{file_path.as_posix()}')
        graphic.clear()
