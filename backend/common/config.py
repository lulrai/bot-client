import os
import re
import time

import psutil
import pymem


class Config():
    def __init__(self, timeout: int = 60, lotro_dir: str = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lord of the Rings Online", debug: bool = False) -> None:
        self.__timeout = timeout
        self.__lotro_base_dir = lotro_dir
        self.__lotro_client = ""
        self.__lotro_exe = ""
        self.__bit_match = re.compile("lotroclient(64)*.exe")
        self.__is_64bits = False
        self.__base_address = 0
        self.__entities_table_address = 0
        self.__entities_table_pattern = ""
        self.__references_table_address = 0
        self.__references_table_pattern = ""
        self.__client_data_address = 0
        self.__client_account_data_pattern = ""
        self.__account_data_address = 0
        self.__storage_data_address = 0
        self.__storage_data_pattern = ""
        self.__pointer_size = 0
        self.__int_size = 0
        self.__map_int_keysize = 0
        self.__bucket_size = 0
        self.__world_entity_offset = 0
        self.__debug = debug
        self.__mem = None
        self.__pid = -1

    def await_process(self) -> None:
        timeout = self.__timeout
        while timeout:
            for proc in psutil.process_iter():
                match = self.__bit_match.match(proc.name().lower())
                if bool(match):
                    if self.__debug: print('Retrieving information from the client process...')
                    time.sleep(1)
                    if self.__debug: print(f'     Client: {match.group(0)}\n     Id: {proc.pid}')
                    self.__pid = proc.pid
                    self.__lotro_client = os.path.join(self.__lotro_base_dir, match.group(0))
                    self.__lotro_exe = match.group(0)
                    self.__is_64bits = (match.group(1) == '64')
                    self.__pointer_size = 8 if self.__is_64bits else 4
                    self.__int_size = 8 if self.__is_64bits else 4
                    self.__map_int_keysize = 8 if self.__is_64bits else 4
                    self.__bucket_size = 24
                    self.__world_entity_offset = 16
                    self.__entities_table_pattern = "48895c2408574883ec40488bd9488b0d?3" if self.__is_64bits else "8B0D?383EC?05633F63BCE"
                    self.__references_table_pattern = "488b05?3488b08488b0cd1428d14c500000000488b4910" if self.__is_64bits else "8B476468DF00000050E8"
                    self.__client_account_data_pattern = "48893d?3b201b900010000" if self.__is_64bits else "85C974078B018B5030FFE2B801000000C3"
                    self.__storage_data_pattern = "4883EC28BA02000000488D0D?3" if self.__is_64bits else "6a016a02b9?3e8"

                    self.__mem = pymem.Pymem(match.group(0))
                    self.__base_address = self.__mem.base_address

                    if self.__debug:
                        print(f'Lotro Client: {self.__lotro_client}')
                        print(f'    Base Address: {self.__base_address}')
                        print(f'    64-bits? {self.__is_64bits}')
                        print(f'    Pointer Size: {self.__pointer_size}')
                        print(f'    Int Size: {self.__int_size}')
                        print(f'    Map Int Size: {self.__map_int_keysize}')
                        print(f'    Bucket Size: {self.__bucket_size}')
                        print(f'    World Entity Offset: {self.__world_entity_offset}')
                    return True
            if self.__debug: print(f'Sleeping for 1 second... Timeout: {timeout}')
            time.sleep(1)
            timeout -= 1
        return False

    def set_address(self) -> None:
        entities_table_offset = 16 if self.__is_64bits else 2
        references_table_offset = 3 if self.__is_64bits else -9
        client_account_data_offset = 3 if self.__is_64bits else -4
        storage_data_offset = 12 if self.__is_64bits else 5

        self.__entities_table_address = self.__set_static_memory_offset(self.__entities_table_pattern, entities_table_offset, 'Entities Table')
        self.__references_table_address = self.__set_static_memory_offset(self.__references_table_pattern, references_table_offset, 'References Table')
        self.__client_data_address = self.__set_static_memory_offset(self.__client_account_data_pattern, client_account_data_offset, 'Client/Account Data')
        self.__account_data_address = self.__client_data_address
        self.__storage_data_address = self.__set_static_memory_offset(self.__storage_data_pattern, storage_data_offset, 'Storage Data')


    def __set_static_memory_offset(self, pattern_type: str, offset: int, mem_type: str) -> hex:
        pattern_pairs = [pattern_type[i:i+2] for i in range(0, len(pattern_type), 2)]
        pattern_regex = b''
        for pair in pattern_pairs:
            if pair[0] == '?':
                for _ in range(int(pair[1])+1):
                    pattern_regex += b'[\x00-\xFF]'
            else:
                pattern_regex += bytes.fromhex(pair)
        
        with open(self.__lotro_client, 'rb') as f:
            file_bytes = f.read()
        matches = re.search(pattern_regex, file_bytes)
        if matches is None: 
            raise Exception(f"No static memory offset found for {mem_type} with pattern: {pattern_type}")
        index = matches.start() + offset
        if self.__debug: 
            print(f'{mem_type} Offset: {index}')

        address_byte_string = file_bytes[index:index+4]
        address_byte_array = bytearray(address_byte_string)
        address_byte_array.reverse()

        address_hex = address_byte_array.hex()
        return address_hex

    def close_mem(self) -> None:
        self.__mem.close_process()

    @property
    def is_64bits(self) -> bool:
        return self.__is_64bits

    @property
    def lotro_client(self) -> str:
        return self.__lotro_client

    @property
    def lotro_exe(self) -> str:
        return self.__lotro_exe

    @property
    def lotro_client_dir(self) -> str:
        return self.__lotro_base_dir

    @property
    def base_address(self) -> int:
        return self.__base_address

    @property
    def entities_table_address(self) -> hex:
        return self.__entities_table_address

    @property
    def references_table_address(self) -> hex:
        return self.__references_table_address

    @property
    def client_data_address(self) -> hex:
        return self.__client_data_address

    @property
    def account_data_address(self) -> hex:
        return self.__account_data_address

    @property
    def storage_data_address(self) -> hex:
        return self.__storage_data_address

    @property
    def pointer_size(self) -> int:
        return self.__pointer_size

    @property
    def int_size(self) -> int:
        return self.__int_size

    @property
    def map_int_keysize(self) -> int:
        return self.__map_int_keysize

    @property
    def bucket_size(self) -> int:
        return self.__bucket_size

    @property
    def world_entity_offset(self) -> int:
        return self.__world_entity_offset

    @property
    def reference_count_size(self) -> int:
        return self.__pointer_size + self.__int_size

    @property
    def mem(self) -> pymem:
        return self.__mem
    
    @property
    def pid(self) -> int:
        return self.__pid