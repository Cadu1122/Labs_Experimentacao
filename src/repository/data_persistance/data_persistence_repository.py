import csv
from datetime import date, datetime
from pathlib import Path
from typing import Callable
from src.repository.data_persistance.models.serialize_rules import SerializeRule

class DataPersistanceRepository:
    
    def persist_data_in_csv(
        self,
        file_path: Path,
        columns: tuple[SerializeRule],
        data: list[dict]
    ):
        '''
         ---
         Receive a dict and parse all data to a csv
         --- 
         Params:
            - file_path: The path to the file
            - columns: A tuple containing columns and their rules to deserialize
            - data: A list of dicts
         ---
         Return:
            None
         ---
         Disclaimer:\n
            Be aware tha this function has limitations in terms of data deserialization...\n
            The MAX that it can go inside of a dict is the following to get VALUE
            >>> {'foo': VALUE }
            >>> {'foo': {'bar': {'baz': {...} } } }
            >>> {'foo': {'bar': [ {'baz':  VALUE} ] } }
        '''
        column_names = [colum.column_name for colum in columns]
        rows = self.__transform_data_in_row(
            columns,
            data
        )
        with open(file_path, 'w+', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_names)
            csv_writer.writerows(rows)

    def get_persited_data_in_csv(
        self,
        file_path: Path,
        mapper_function: Callable[[tuple[any], tuple[str]], any] = None
    ):
        result: list[dict] = []
        mapper_function = mapper_function if mapper_function else self.__transform_row_in_data
        with open(file_path,  'r') as f:
            csv_reader = csv.reader(f)
            columns = next(csv_reader)
            for row in csv_reader:
                result.append(mapper_function(row, columns))
        return result
    
    def get_persited_data_in_csv_generator_version(
        self,
        file_path: Path
    ):
        mapper_function = mapper_function if mapper_function else self.__transform_row_in_data
        with open(file_path,  'r') as f:
            csv_reader = csv.reader(f)
            next(csv_reader)
            for row in csv_reader:
                yield row

    
    def __transform_row_in_data(
        self,
        row: tuple[any],
        columns: tuple[str]
    ):
        result = {}
        for i,column_name in enumerate(columns):
            value = row[i]
            if ';' in value:
                value = ';'.join(value)
            result[column_name] = value
        return result


    def __transform_data_in_row(
        self, 
        columns: tuple[SerializeRule],
        data: list[dict]
    ):
        '''
            Given a set of columns and values it desirialize the data
            and map it to a valid csv row
            ---
            Disclaimer: Array are transformed in strings with the values separed by a semicolon ( ; )
        '''
        rows = []
        for value in data:
            row_values = []
            for column in columns:
                row_values.append(
                    self.__get_attribute_by_deserialize_rule(
                        value, 
                        deserialize_rule=column.dict_deserialize_rule
                    )
                )
            rows.append(row_values)
        return rows

    def __get_attribute_by_deserialize_rule(
        self, 
        data: dict, 
        deserialize_rule: tuple[str]
    ):
        def safe_get_value(value, path):
            value = value.get(path)
            if isinstance(value, date) or isinstance(value, datetime):
                return value.isoformat()
            return value

        latest_obtained_value = data
        accumulated_list_values = []
        for data_path in deserialize_rule:
            if latest_obtained_value:
                if isinstance(latest_obtained_value, list):
                    for value in latest_obtained_value:
                        accumulated_list_values.append(safe_get_value(value, data_path))
                else:
                    latest_obtained_value = safe_get_value(latest_obtained_value, data_path)
            else:
                break
        if accumulated_list_values:
            return ';'.join(accumulated_list_values)
        if latest_obtained_value == []:
            return None
        return latest_obtained_value