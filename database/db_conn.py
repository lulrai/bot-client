""" Module for database connection. """
import os
import json
import requests

class DBConnection():
    """ Database connection class. """
    def __init__(self) -> None:
        """
        Initialize the database connection.
        """
        self.__db_master_key = os.getenv('DB_MASTERKEY')
        self.__db_create_path = os.getenv('DB_CREATEPATH')
        self.__db_update_path = os.getenv('DB_UPDATEPATH')
        self.__db_read_path = os.getenv('DB_READPATH')
        self.__db_delete_path = os.getenv('DB_DELETEPATH')

    def create(self, data: dict, file_name: str, private: bool = True) -> dict:
        """
        Create a new entry in the database.

        Parameters
        ----------
        data : dict
            The data to be sent to the database.
        file_name : str
            The name of the file to be created.
        private : bool, optional
            Whether the file should be private or not, by default True

        Returns
        -------
        dict
            The response from the database.
        """
        response = requests.post(
            url = self.__db_create_path,
            data={
                'private': private,
                'content': json.dumps(data, indent=4),
                'fileName': file_name
            },
            headers={'x-gist-master-key': self.__db_master_key},
            timeout=30)
        return response.json()

    def update(self, data: dict, json_id: str) -> dict:
        """
        Update an existing entry in the database.

        Parameters
        ----------
        data : dict
            The data to be sent to the database.
        json_id : str
            The json id of the entry to be updated.

        Returns
        -------
        dict
            The response from the database.
        """
        response = requests.put(
            url = self.__db_update_path,
            params={'jsonId': json_id},
            data={
                'content': json.dumps(data, indent=4),
            },
            headers={'x-gist-master-key': self.__db_master_key},
            timeout=30)
        return response.json()

    def read(self, json_id: str) -> dict:
        """
        Read an existing entry in the database.

        Parameters
        ----------
        json_id : str
            The json id of the entry to be read.

        Returns
        -------
        dict
            The data in the database of the given entry.
        """
        response = requests.get(
            url = self.__db_read_path,
            params={'jsonId': json_id},
            headers={'x-gist-master-key': self.__db_master_key},
            timeout=30)
        return response.json()

    def delete(self, json_id: str) -> dict:
        """
        Delete an existing entry in the database.

        Parameters
        ----------
        json_id : str
            The json id of the entry to be deleted.

        Returns
        -------
        dict
            The response from the database.
        """
        response = requests.delete(
            url = self.__db_delete_path,
            params={'jsonId': json_id},
            headers={'x-gist-master-key': self.__db_master_key},
            timeout=30)
        return response.json()
        