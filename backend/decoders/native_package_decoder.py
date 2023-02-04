from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.common.data_types import BitSet, Position
from backend.decoders.friend_adaptor_decoder import FriendAdaptorDecoder
from backend.decoders.hash_decoder import ContainersDecoder
from backend.decoders.ignore_adaptor_decoder import IgnoreAdaptorDecoder
from backend.decoders.native_decoder import MiscNativesDecoder
from backend.decoders.properties_decoder import PropertiesDecoder
from backend.properties.properties_set import Properties
from backend.properties.properties_val import PropertyValue
from backend.strings.string_info_utils import StringInfoUtils
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class NativePackagesDecoder():
    def __init__(self, config: GameConfig, data_facade: DataFacade) -> None:
        self.__config: GameConfig = config
        self.__data_facade: DataFacade = data_facade
        self.__properties_decoder: PropertiesDecoder = PropertiesDecoder(config, data_facade)
        self.__containers_decoder: ContainersDecoder = ContainersDecoder(config)
        self.__misc_decoder: MiscNativesDecoder = MiscNativesDecoder(config, data_facade)
        self.__friends_decoder: FriendAdaptorDecoder = FriendAdaptorDecoder(config, data_facade)
        self.__ignores_decoder: IgnoreAdaptorDecoder = IgnoreAdaptorDecoder(config, data_facade)

    def handle_native(self, package_factory_ptr: int, native_package_ptr: int) -> object:
        props: Properties = None
        package_id = self.__config.mem.read_uint(package_factory_ptr)
        raw_size = self.__config.mem.read_uint(package_factory_ptr+4)
        flags = self.__config.mem.read_uint(package_factory_ptr+8)

        if package_id == 166: return self.__handle_properties(native_package_ptr, raw_size)
        elif package_id == 52: return self.__handle_db_properties(native_package_ptr, raw_size)
        elif package_id == 39: return self.__handle_base_property(native_package_ptr, raw_size)
        elif package_id == 199: return self.__handle_string_info(native_package_ptr, raw_size)
        elif package_id == 225: return self.__handle_string(native_package_ptr, raw_size)
        elif package_id == 160: return self.__handle_position(native_package_ptr, raw_size)
        elif package_id in (17, 176, 104): return self.__containers_decoder.handle_array(native_package_ptr, package_id)
        elif package_id in (25, 182, 111): return self.__containers_decoder.handle_list(native_package_ptr, package_id)
        elif package_id in (11, 35): return self.__containers_decoder.handle_inint_hashtable(native_package_ptr, package_id)
        elif package_id == 23: return self.__containers_decoder.handle_intlong_hashtable(native_package_ptr, package_id)
        elif package_id in (117, 97): return self.__containers_decoder.handle_longint_hashtable(native_package_ptr, package_id)
        elif package_id == 18: return self.__containers_decoder.handle_int_set(native_package_ptr, package_id)
        elif package_id == 105: return self.__containers_decoder.handle_long_set(native_package_ptr, package_id)
        elif package_id in (13, 37): return self.__containers_decoder.handle_intmulti_hashtable(native_package_ptr, package_id)
        elif package_id == 138: return self.__containers_decoder.handle_NRHash(native_package_ptr, package_id)
        elif package_id == 134: return self.__containers_decoder.handle_NHashSet(native_package_ptr, package_id)
        elif package_id == 57: return self.__handle_dynamic_bitset(native_package_ptr, package_id, raw_size)
        elif package_id == 3103: return self.__misc_decoder.handle_bank_repository_data(native_package_ptr, raw_size)
        elif package_id == 2567: return self.__misc_decoder.handle_bank_repository_data_adaptor(native_package_ptr, raw_size)
        elif package_id == 403: return self.__misc_decoder.handle_currency_record(native_package_ptr, raw_size)
        elif package_id == 407: return self.__misc_decoder.handle_discovered_mapnote_data(native_package_ptr, raw_size)
        elif package_id == 414: return self.__friends_decoder.handle_friend_adaptor(native_package_ptr, raw_size)
        elif package_id == 433: return self.__ignores_decoder.handle_ignore_adaptor(native_package_ptr, raw_size)
        else:
            print('Unmanaged native: package_id=', package_id)
            return None

    def __handle_db_properties(self, native_package_ptr: int, size: int) -> Properties:
        ptr: int = self.__config.mem.read_uint(native_package_ptr)
        size: int = self.__config.pointer_size * 5 + 8
        return self.__handle_db_properties(ptr, size)

    def __handle_properties(self, properties_ptr: int, size: int) -> Properties:
        return self.__properties_decoder.handle_properties(properties_ptr, self.__config.pointer_size)

    def __handle_base_property(self, native_package_ptr: int, size: int) -> PropertyValue:
        return self.__properties_decoder.handle_property(native_package_ptr, 0, None)

    def __handle_string(self, native_package_ptr: int, size: int) -> str:
        str_ptr: int = self.__config.mem.read_uint(native_package_ptr)
        return Utils.retrieve_string(self.__config.mem, str_ptr)

    def __handle_string_info(self, native_package_ptr: int, size: int) -> str:
        return StringInfoUtils.read_string_info(self.__config, self.__data_facade, native_package_ptr, 0)

    def __handle_position(self, native_package_ptr: int, size: int) -> Position:
        return Position.from_mem(self.__config, native_package_ptr, 0)

    def __handle_dynamic_bitset(self, native_package_ptr: int, package_id: int, size: int) -> BitSet:
        return Utils.read_arb_bitfield(self.__config, native_package_ptr, 0)
