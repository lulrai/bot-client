"""
GameConfig class used to store all the configuration data for the game and program.
"""
from __future__ import annotations
import os
import re
import logging

from enum import Enum
import configparser

import pymem
import yaml

from backend.utils.common_utils import Utils

Client_Status = Enum('Client_Status', ['NOT_FOUND', 'RUNNING', 'MISSING_ADMIN', 'UNKNOWN_ERROR'])

class GameConfig():
    """
    GameConfig class properties and methods to retrieve the data from in-game.
    """

    def __init__(self, app_config: AppConfig, debug: bool = True) -> None:
        """
        Initialize the GameConfig class.
        :param timeout: The timeout in seconds to wait for the game process to start.
        :type timeout: int
        :param lotro_dir: The directory where the game is installed.
        :type lotro_dir: str
        :param debug: Whether to enable debug mode or not.
        :type debug: bool
        :returns: None
        """
        # self.__timeout: int = timeout # Timeout in seconds to wait for the game process to start.
        # self.__update_window: customtkinter.CTk = update_window # The update window to update the progress bar.
        self.__lotro_base_dir: str = app_config.get_config('lotro', 'base_dir') # The directory where the game is installed.
        self.__lotro_pref_path: str = app_config.get_config('pref', 'default_path') # The path to the lotro config file.
        self.__client_status: Client_Status = Client_Status.NOT_FOUND # The status of reading of the game client.
        self.__lotro_client: str = "" # The path to the game client.
        self.__lotro_exe: str = "" # The exe of the game client.
        self.__is_64bits: bool = False # Whether the game client is 64-bits or not.
        self.__debug: bool = debug # Whether to enable debug mode or not.
        self.__mem: pymem = None # The pymem object to read the game client memory.
        self.__pid: int = -1 # Keep track of the game client process id.
        self.__preferences_ini: configparser.ConfigParser = configparser.ConfigParser() # The preferences.ini file loader.
        self.__preferences_ini.read(self.__lotro_pref_path) # Read the preferences.ini file.

        self.__base_address: int = 0 # The base address of the game client.
        self.__entities_table_address: int = 0 # The address of the entities table.
        self.__entities_table_pattern: str = "" # The pattern to find the entities table.
        self.__references_table_address: int = 0 # The address of the references table.
        self.__references_table_pattern: str = "" # The pattern to find the references table.
        self.__client_data_address: int = 0 # The address of the client data.
        self.__client_account_data_pattern: str = "" # The pattern to find the client data.
        self.__account_data_address: int = 0 # The address of the account data.
        self.__storage_data_address: int = 0 # The address of the storage data.
        self.__storage_data_pattern: str = "" # The pattern to find the storage data.

        self.__pointer_size: int = 0 # The size of a pointer in the game client memory.
        self.__int_size: int = 0 # The size of an int in the game client memory.
        self.__map_int_keysize: int = 0 # The size of an int in the game client memory.
        self.__bucket_size: int = 0 # The size of a bucket in the game client memory.
        self.__world_entity_offset: int = 0 # The offset of the world entity in the entities table.

    def set_address(self, name_match: re.Match, pid: int) -> None:
        """
        Set the addresses of the entities table, references table, client data and storage data.
        :returns: None
        """
        # If the client info has already been retrieved.
        if self.__client_status == Client_Status.RUNNING:
            return

        # If the client info has not already been retrieved, retrieve the information from the client process.
        if self.__debug:
            logging.info('Retrieving information from the client process...')
        if self.__debug:
            logging.info('\tClient: %s\n\tId: %d', name_match.group(0), pid)
        try:
            self.__pid = pid
            self.__is_64bits = (name_match.group(1) == '64')
            self.__lotro_client = os.path.join(self.__lotro_base_dir, 'x64', 'lotroclient64.exe') if self.__is_64bits else os.path.join(self.__lotro_base_dir, 'lotroclient.exe')
            self.__lotro_exe = name_match.group(0)
            self.__pointer_size = 8 if self.__is_64bits else 4
            self.__int_size = 8 if self.__is_64bits else 4
            self.__map_int_keysize = 8 if self.__is_64bits else 4
            self.__bucket_size = 24
            self.__world_entity_offset = 16
            self.__entities_table_pattern = "48895c2408574883ec40488bd9488b0d?3" if self.__is_64bits else "8B0D?383EC?05633F63BCE"
            self.__references_table_pattern = "488b05?3488b08488b0cd1428d14c500000000488b4910" if self.__is_64bits else "8B476468DF00000050E8"
            self.__client_account_data_pattern = "48893d?3b201b900010000" if self.__is_64bits else "85C974078B018B5030FFE2B801000000C3"
            self.__storage_data_pattern = "4883EC28BA02000000488D0D?3" if self.__is_64bits else "6a016a02b9?3e8"

            self.__mem = pymem.Pymem(name_match.group(0)) # Create a pymem object to read the game client memory.
            self.__base_address = self.__mem.base_address + (4096 - 1024) if self.__is_64bits else 0 # Get the base address of the game client.
            if self.__debug: # If debug mode is enabled, print some useful info.
                logging.info('Lotro Client: %s}', self.__lotro_client)
                logging.info('\tBase Address: %d', self.__base_address)
                logging.info('\t64-bits? %r', self.__is_64bits)
                logging.info('\tPointer Size: %d', self.__pointer_size)
                logging.info('\tInt Size: %d', self.__int_size)
                logging.info('\tMap Int Size: %d', self.__map_int_keysize)
                logging.info('\tBucket Size: %d', self.__bucket_size)
                logging.info('\tWorld Entity Offset: %d', self.__world_entity_offset)

            entities_table_offset = 16 if self.__is_64bits else 2 # The offset of the entities table.
            references_table_offset = 3 if self.__is_64bits else -9 # The offset of the references table.
            client_account_data_offset = 3 if self.__is_64bits else -4 # The offset of the client data.
            storage_data_offset = 12 if self.__is_64bits else 5 # The offset of the storage data.
            preferences_ini_offset = 0x19F8 if self.__is_64bits else 0x40

            self.__entities_table_address = self.__set_static_memory_offset(self.__entities_table_pattern, entities_table_offset, 'Entities Table')
            self.__references_table_address = self.__set_static_memory_offset(self.__references_table_pattern, references_table_offset, 'References Table')
            self.__client_data_address = self.__set_static_memory_offset(self.__client_account_data_pattern, client_account_data_offset, 'Client/Account Data')
            self.__account_data_address = self.__client_data_address
            self.__storage_data_address = self.__set_static_memory_offset(self.__storage_data_pattern, storage_data_offset, 'Storage Data')

            if self.__debug:
                logging.debug('Preferences located at with offset: %s', hex(self.__client_data_address + preferences_ini_offset))
            main_client_data_addr = Utils.get_pointer(self.__mem, self.__client_data_address, self.__pointer_size) if not self.__is_64bits else self.__client_data_address
            preferences_addr = Utils.get_pointer(self.__mem, main_client_data_addr + preferences_ini_offset, self.__pointer_size)
            self.__lotro_pref_path = Utils.retrieve_string(self.__mem, preferences_addr)
            if self.__debug:
                logging.info('Preferences path: %s', self.__lotro_pref_path)
            self.__preferences_ini.read(self.__lotro_pref_path)
            self.__client_status = Client_Status.RUNNING
        except pymem.pymem.exception.CouldNotOpenProcess as could_not_open: # Could not access the client memory (probably not running as admin)
            self.__client_status = Client_Status.MISSING_ADMIN
            logging.exception(could_not_open)
        except Exception as gen_exception: # pylint: disable=broad-except
            self.__client_status = Client_Status.UNKNOWN_ERROR
            logging.exception(gen_exception) # Log the exception
            raise gen_exception

    def __set_static_memory_offset(self, pattern_type: str, offset: int, mem_type: str) -> int:
        """
        Set the address of a static memory offset.
        :param pattern_type: The pattern to find the memory offset.
        :type pattern_type: str
        :param offset: The offset of the memory address.
        :type offset: int
        :param mem_type: The type of memory.
        :type mem_type: str
        :returns: The address of the memory offset in int.
        :rtype: int
        """
        pattern_pairs = [pattern_type[i:i+2] for i in range(0, len(pattern_type), 2)] # Split the pattern into pairs.
        pattern_regex = bytearray() # The regex pattern to find the memory offset.
        for pair in pattern_pairs: # Iterate over the pattern pairs.
            if pair[0] == '?': # If the pair is a wildcard.
                for _ in range(int(pair[1])+1): # Iterate over the wildcard.
                    pattern_regex.extend(b'[\x00-\xFF]') # Add the wildcard to the regex pattern.
            else: # If the pair is not a wildcard.
                pattern_regex.extend(re.escape(bytes.fromhex(pair))) # Add the pair to the regex pattern.
        
        compiled_pattern_regex = re.compile(bytes(pattern_regex)) # Compile the regex pattern.
        with open(self.__lotro_client, 'rb') as game_client: # Open the game client exe.
            file_bytes = game_client.read() # Read the game client exe.
        matches = compiled_pattern_regex.search(file_bytes) # Find the memory offset.
        if matches is None: # If the memory offset is not found.
            raise Exception(f"No static memory offset found for {mem_type} with pattern: {pattern_type}") # Raise an exception.
        
        index = matches.start() # Get the index of the memory offset.
        
        address_byte_string = file_bytes[index+offset:index+offset+4] # Get the address bytes.
        address_byte_array = bytearray(address_byte_string) # Convert the address bytes to a byte array.
        address_int = int.from_bytes(address_byte_array, byteorder='little') # Convert the address bytes to an int.
        
        address_int = (index+offset+4) + address_int if self.__is_64bits else address_int
                
        if self.__debug: # If debug mode is enabled, print some useful info.
            print(f'{mem_type} Address: \n\tHex: {hex(address_int)}\n\tInt: {address_int}\n\tWith Base Address: {address_int+self.__base_address}') # Print the memory offset.
            
        return self.__base_address + address_int # Return the address as an int.

    def close_mem(self) -> None:
        """
        Close the pymem object.
        :returns: None
        """
        self.__mem.close_process()

    @property
    def is_64bits(self) -> bool:
        """
        Get the 64-bits property.
        :returns: The 64-bits property.
        :rtype: bool
        """
        return self.__is_64bits

    @property
    def lotro_client(self) -> str:
        """
        Get the lotro client property.
        :returns: The lotro client property.
        :rtype: str
        """
        return self.__lotro_client

    @property
    def lotro_exe(self) -> str:
        """
        Get the lotro exe property.
        :returns: The lotro exe property.
        :rtype: str
        """
        return self.__lotro_exe

    @property
    def lotro_client_dir(self) -> str:
        """
        Get the lotro client dir property.
        :returns: The lotro client dir property.
        :rtype: str
        """
        return self.__lotro_base_dir

    @property
    def base_address(self) -> int:
        """
        Get the base address property.
        :returns: The base address property.
        :rtype: int
        """
        return self.__base_address

    @property
    def entities_table_address(self) -> int:
        """
        Get the entities table address property.
        :returns: The entities table address property.
        :rtype: int
        """
        return self.__entities_table_address

    @property
    def references_table_address(self) -> int:
        """
        Get the references table address property.
        :returns: The references table address property.
        :rtype: int
        """
        return self.__references_table_address

    @property
    def client_data_address(self) -> int:
        """
        Get the client data address property.
        :returns: The client data address property.
        :rtype: int
        """
        return self.__client_data_address

    @property
    def account_data_address(self) -> int:
        """
        Get the account data address property.
        :returns: The account data address property.
        :rtype: int
        """
        return self.__account_data_address

    @property
    def storage_data_address(self) -> int:
        """
        Get the storage data address property.
        :returns: The storage data address property.
        :rtype: int
        """
        return self.__storage_data_address

    @property
    def pointer_size(self) -> int:
        """
        Get the pointer size property.
        :returns: The pointer size property.
        :rtype: int
        """
        return self.__pointer_size

    @property
    def int_size(self) -> int:
        """
        Get the int size property.
        :returns: The int size property.
        :rtype: int
        """
        return self.__int_size

    @property
    def map_int_keysize(self) -> int:
        """
        Get the map int keysize property.
        :returns: The map int keysize property.
        :rtype: int
        """
        return self.__map_int_keysize

    @property
    def bucket_size(self) -> int:
        """
        Get the bucket size property.
        :returns: The bucket size property.
        :rtype: int
        """
        return self.__bucket_size

    @property
    def world_entity_offset(self) -> int:
        """
        Get the world entity offset property.
        :returns: The world entity offset property.
        :rtype: int
        """
        return self.__world_entity_offset

    @property
    def reference_count_size(self) -> int:
        """
        Get the reference count size property.
        :returns: The reference count size property.
        :rtype: int
        """
        return self.__pointer_size + self.__int_size

    @property
    def mem(self) -> pymem:
        """
        Get the pymem object.
        :returns: The pymem object.
        :rtype: pymem
        """
        return self.__mem
    
    @property
    def pid(self) -> int:
        """
        Get the process id.
        :returns: The process id.
        :rtype: int
        """
        return self.__pid
    
    @property
    def debug(self) -> bool:
        """
        Get the debug property.
        :returns: The debug property.
        :rtype: bool
        """
        return self.__debug
    
    @property
    def pref_ini(self) -> configparser.ConfigParser:
        """
        Get the pref ini property.
        :returns: The pref ini property.
        :rtype: str
        """
        return self.__preferences_ini
    
    @property
    def lotro_pref_path(self) -> str:
        """
        Get the lotro pref path property.
        :returns: The lotro pref path property.
        :rtype: str
        """
        return self.__lotro_pref_path
    
    @property
    def client_status(self) -> str:
        """
        Get the client status property.
        :returns: The client status property.
        :rtype: str
        """
        return self.__client_status
    @client_status.setter
    def client_status(self, value: str) -> None:
        """
        Set the client status property.
        :returns: None
        """
        self.__client_status = value

class AppConfig():
    """
    A class to store the application config.
    """
    def __init__(self) -> None:
        self.__config_dir = os.path.join(os.getenv('APPDATA'), 'LoDE') # Get the application data directory.
        # Create the config directory if it doesn't exist.
        if not os.path.exists(self.__config_dir):
            os.makedirs(self.__config_dir)
        self.__config_file = self.__ensure_config_exists(self.__config_dir, 'app_config.yaml')

    def __ensure_config_exists(self, config_dir: str, config_file: str) -> dict:
        """
        Create the config file.
        :returns: None
        """
        # Get the config file path.
        config_path = os.path.join(config_dir, config_file) # Get the config file path.
        # Check if the config file exists.
        if os.path.exists(config_path):
            # Load the config file.
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
            return config
        # Create the default config.
        default_config = {
            'debug': False,
            'start_minimized': False,
            'start_with_windows': False,
            'theme': 'dark',
            'log': {
                'level': 'INFO',
                'folder': os.path.join(self.__config_dir, 'logs'),
                'backup_count': 10
            },
            'lotro': {
                'base_dir': 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lord of the Rings Online',
                'client_check_interval': 60
            },
            'pref': {
                'backup_count': 30,
                'default_path': f"C:\\Users\\{os.getenv('USERNAME')}\\Documents\\The Lord of the Rings Online\\UserPreferences.ini"
                #'default_path': f"C:\\Users\\{os.getenv('USERNAME')}\\Documents\\The Lord of the Rings Online\\Test.ini"
            },
            'sync': {
                'interval': 60,
                'sync_on_start': True
            }
        }
        # Write the config to file.
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(default_config, file)
        # Return the default config.
        return default_config

    def get_config(self, key: str, subkey: str = None) -> str:
        """
        Get a config value.
        :param key: The config key.
        :type key: str
        :returns: The config value.
        :rtype: str
        """
        if subkey:
            return self.__config_file[key][subkey]
        return self.__config_file[key]

    def set_config(self, value: str, key: str, subkey: str = None) -> None:
        """
        Set a config value.
        :param key: The config key.
        :type key: str
        :param value: The config value.
        :type value: str
        :returns: None
        """
        if subkey:
            self.__config_file[key][subkey] = value
        else:
            self.__config_file[key] = value
        # Write the config to file.
        with open(os.path.join(self.__config_dir, 'app_config.yaml'), 'w', encoding='utf-8') as file:
            yaml.dump(self.__config_file, file)
