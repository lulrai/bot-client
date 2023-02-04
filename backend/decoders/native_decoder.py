from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.common.data_types import BitSet
from backend.common.vault_data import VaultDescriptor, VaultItemDescriptor
from backend.decoders.hash_decoder import HashtableDecoder
from backend.decoders.properties_decoder import PropertiesDecoder
from backend.managers.abstract_mappers import EnumMapper
from backend.properties.properties_set import Properties
from backend.properties.properties_val import PropertyValue
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class MiscNativesDecoder():
    def __init__(self, config: GameConfig, data_facade: DataFacade) -> None:
        self.__config: GameConfig = config
        self.__data_facade = data_facade
        self.__props_decoder: PropertiesDecoder = PropertiesDecoder(config, data_facade)
        
    class VaultDescriptorDecoder(HashtableDecoder):
        def __init__(self, config: GameConfig) -> None:
            super().__init__(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, config.pointer_size)

        def parse_key(self, hash_table_data_ptr: int) -> int:
            return self.__config.mem.read_uint(hash_table_data_ptr)

        def parse_value(self, result_map: dict[int, str], hash_table_data_ptr: int, val_offset: int, package_id: int) -> str:
            utf16_str_ptr = self.__config.mem.read_uint(hash_table_data_ptr+val_offset)
            return Utils.retrieve_string(self.__config.mem, utf16_str_ptr)

    class CurrencyRecordDecoder(HashtableDecoder):
        def __init__(self, config: GameConfig) -> None:
            super().__init__(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, 4)

        def parse_key(self, hash_table_data_ptr: int) -> int:
            return self.__config.mem.read_uint(hash_table_data_ptr)

        def parse_value(self, result_map: dict[int, str], hash_table_data_ptr: int, val_offset: int, package_id: int) -> str:
            return self.__config.mem.read_uint(hash_table_data_ptr+val_offset)

    def __decode_map_notes(self, buffer: bytearray) -> list[str]:
        enum_mapper: EnumMapper = self.__data_facade.get_enums_manager().get_enum_mapper(587202671)
        result: list[str] = []
        nb_bits = len(buffer) * 8
        bit_set: BitSet = BitSet.from_bytearray(buffer, nb_bits)
        for i in range(len(bit_set)):
            item_str: str = enum_mapper.get_str(i)
            if item_str:
                known: bool = bit_set.get(i)
                if known: result.append(item_str)
        return result

    def handle_bank_repository_data(self, native_package_ptr: int, raw_size: int) -> VaultDescriptor:
        decode: self.VaultDescriptorDecoder = self.VaultDescriptorDecoder(self.__config)
        chests: dict[int, str] = decode.decode_hash_table(native_package_ptr, self.__config.pointer_size, 0)
        result: VaultDescriptor = VaultDescriptor()
        for chest_id in chests:
            result.add_chest(chest_id, chests.get(chest_id))
        return result

    def handle_bank_repository_data_adaptor(self, native_package_ptr: int, raw_size: int) -> VaultItemDescriptor:
        item_iid: int = self.__config.mem.read_long(native_package_ptr+8)
        props_offset: int = 24 if self.__config.is_64bits else 20
        props: Properties = self.__props_decoder.handle_properties(native_package_ptr, props_offset)
        tooltip_prop_offset: int = 112 if self.__config.is_64bits else 72
        prop_val: PropertyValue = self.__props_decoder.handle_property(native_package_ptr, tooltip_prop_offset, None)
        return VaultItemDescriptor(item_iid, props, prop_val)

    def handle_currency_record(self, native_package_ptr: int, raw_size: int) -> tuple[int]:
        decoder: self.CurrencyRecordDecoder = self.CurrencyRecordDecoder(self.__config)
        data: dict[int, int] = decoder.decode_hash_table(native_package_ptr, 0, 0)
        copper: int = data.get(1879048730)
        copper = copper if copper else 0
        silver: int = data.get(1879048729)
        silver = silver if silver else 0
        gold: int = data.get(1879048728)
        gold = gold if gold else 0
        return (gold, silver, copper)

    def handle_discovered_mapnote_data(self, native_package_ptr: int, raw_size: int) -> list[str]:
        ptr: int = self.__config.mem.read_uint(native_package_ptr)
        nb_bits: int = 2048
        size: int = nb_bits // 8
        bitset_array: bytearray = bytearray(self.__config.mem.read_bytes(ptr, size))
        return self.__decode_map_notes(bitset_array)