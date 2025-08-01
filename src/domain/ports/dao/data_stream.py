"""
A port to create adapters for data stream, being capable of performing pull, push and update operations.
"""
from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame


class DataStream(ABC):
    """
    Create adapters for persistence, being capable of performing pull, push and update operations.
    """

    def __init__(self):
        self.exception: str = ''

    @abstractmethod
    def pull(
            self,
            args: dict
    ) -> DataFrame:
        """
        Launch a query to get data from a data source stipulated at the arguments.
        :param args: data to be used to create the connection and launch the query
        :return: the data that has been recovered from the source
        """
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    def push(
            self,
            data: Any,
            args: dict
    ) -> bool:
        """
        Launch a query to insert data into a data source stipulated at the arguments.
        :param data: the data to be inserted
        :param args: data to be used to create the connection and launch the query
        :return: True if query has been successfully executed, False otherwise
        """
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    def update(
            self,
            field: str,
            old,
            new,
            args: dict,
            comparator: str = '=='
    ) -> bool:
        """
        Launch a query to update data in a data source stipulated at the arguments.
        :param field: the id of the field to update
        :param old: the target configuration to be updated
        :param new: the value replacing the target
        :param args: data to be used to create the connection and launch the query
        :param comparator: the operation comparator to be used to update
        :return: True if query has been successfully executed, False otherwise
        """
        raise NotImplementedError("Method not implemented at the abstract level.")