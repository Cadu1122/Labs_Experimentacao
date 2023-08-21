import csv
from pathlib import Path

from projeto_1.repository.data_persistance.models.column import Column

class DataPersistanceRepository:
    
    def persist_data_in_csv(
        self,
        file_path: Path,
        columns: tuple[Column],
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
        column_names = [colum.name for colum in columns]
        rows = self.__transform_data_dict_in_row(
            columns,
            data
        )
        with open(file_path, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_names)
            csv_writer.writerows(rows)
    
    def __transform_data_dict_in_row(
        self, 
        columns: tuple[Column],
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
        latest_obtained_value = data
        accumulated_list_values = []
        for data_path in deserialize_rule:
            if latest_obtained_value:
                if type(latest_obtained_value) == list:
                    for value in latest_obtained_value:
                        accumulated_list_values.append(value.get(data_path))
                else:
                    latest_obtained_value = latest_obtained_value.get(data_path)
            else:
                break
        if accumulated_list_values:
            return ';'.join(accumulated_list_values)
        if latest_obtained_value == []:
            return None
        return latest_obtained_value