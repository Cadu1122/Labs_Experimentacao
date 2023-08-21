from dataclasses import dataclass


@dataclass
class Column:
    name: str
    dict_deserialize_rule: tuple[str]
    '''
        A tuple with the path of some value inside a dict\n
        ---
        Example:
        >>> foo = {'k1': {'k2': [ {'k3': VALUE} ] } }
        >>> dict_deserialize_rule = ('k1', 'k2', 'k3)
    '''