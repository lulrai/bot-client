from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.decoders.properties_decoder import PropertiesDecoder
from backend.properties.properties_set import Properties
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class ClientData():
    def __init__(self, config: GameConfig, facade: DataFacade, debug: bool = True) -> None:
        self.__config: GameConfig = config
        self.__properties_decoder: PropertiesDecoder = PropertiesDecoder(config, facade)
        self.__debug: bool = debug
        self.__server_name: str = ""
        self.__language: str = ""
        self.__account_property: Properties = None
        self.__world_property: Properties = None

    def load_client_data(self) -> ClientData:
        try:
            client_instance_addr = Utils.get_pointer(self.__config.mem, self.__config.client_data_address, self.__config.pointer_size)

            server_name_offset = 0x130 if self.__config.is_64bits else 0xb4
            language_offset = 0xf0 if self.__config.is_64bits else 0x84
            account_property_offset = 0x190 if self.__config.is_64bits else 0xe8
            world_property_offset = 0x188 if self.__config.is_64bits else 0xe4

            server_name_addr = Utils.get_pointer(self.__config.mem, client_instance_addr + server_name_offset, self.__config.pointer_size)
            self.__server_name = Utils.retrieve_string(self.__config.mem, server_name_addr)

            language_addr = Utils.get_pointer(self.__config.mem, client_instance_addr + language_offset, self.__config.pointer_size)
            self.__language = Utils.retrieve_string(self.__config.mem, language_addr)

            account_property_addr = Utils.get_pointer(self.__config.mem, client_instance_addr + account_property_offset, self.__config.pointer_size)
            acc_data_offset = 0xb8 if self.__config.is_64bits else 0x6c
            self.__account_property: Properties = self.__properties_decoder.handle_properties(account_property_addr, acc_data_offset)

            world_property_addr =  Utils.get_pointer(self.__config.mem, client_instance_addr + world_property_offset, self.__config.pointer_size)
            world_data_offset = 0x20 if self.__config.is_64bits else 0x10
            self.__world_property: Properties = self.__properties_decoder.handle_properties(world_property_addr, world_data_offset)

            return self
        except Exception as exp:
            # raise Exception('Error in client.py!') from exp
            raise exp

    @property
    def server_name(self) -> str:
        return self.__server_name

    @property
    def language(self) -> str:
        return self.__language

    @property
    def account_data(self) -> Properties:
        return self.__account_property

    @property
    def world_data(self) -> Properties:
        return self.__world_property
