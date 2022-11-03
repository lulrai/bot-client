from __future__ import annotations

from typing import TYPE_CHECKING

import pymem
from backend.common.config import Config
from backend.common.data_types import BitSet, Color, Position, Vector3D
from backend.managers.abstract_mappers import EnumMapper
from backend.properties.properties_def import PropertyDef
from backend.properties.properties_set import Properties
from backend.properties.properties_type import PropertyType
from backend.properties.properties_val import ArrayPropertyValue, PropertyValue
from backend.strings.string_info_utils import StringInfoUtils
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class PropertiesDecoder():
    def __init__(self, config: Config, data_facade: DataFacade, debug: bool = False) -> None:
        self.__config = config
        self.__memory: pymem = config.mem
        self.__data_facade: DataFacade = data_facade
        self.__debug: bool = debug

    def load_property_descriptor(self, ptr: int, expected_prop_def: PropertyDef) -> PropertyDef:
        ref_count_size = self.__config.reference_count_size
        property_desc_size = ref_count_size + 8
        prop_id = self.__memory.read_uint(ptr + ref_count_size)
        prop_type = self.__memory.read_uint(ptr + ref_count_size + 4)
        if expected_prop_def:
            assert expected_prop_def.pid == prop_id
            assert expected_prop_def.ptype.val == prop_type
        prop_def = self.__data_facade.get_properties_registry().get_property_def(prop_id)
        return prop_def

    def handle_pointer_prop_val(self, ptr: int, property_def: PropertyDef) -> object:
        p_type = property_def.ptype.val
        if self.__debug: print(f"property type: {property_def.ptype.NAMES[p_type]}")
        if p_type == PropertyType.StringInfo:
            offset = self.__config.reference_count_size
            return StringInfoUtils.read_string_info(self.__config, self.__data_facade, ptr, offset)
        if p_type == PropertyType.String:
            offset = self.__config.reference_count_size
            string_ptr = self.__memory.read_uint(ptr+offset)
            return Utils.retrieve_string(self.__memory, string_ptr, 260)
        if p_type == PropertyType.Array:
            offset = self.__config.reference_count_size
            data_ptr = self.__memory.read_uint(ptr+offset)
            nb_items = self.__memory.read_uint(ptr+offset+self.__config.pointer_size+4)
            values: list[PropertyValue] = []
            if nb_items == 0: return values
            for i in range(nb_items):
                prop_value = self.handle_property(data_ptr, i*2*self.__config.pointer_size, None)
                if prop_value:
                    values.append(prop_value)
            return values
        if p_type == PropertyType.Struct:
            offset = self.__config.reference_count_size
            return self.handle_properties(ptr, offset)
        if p_type == PropertyType.Bitfield32:
            offset = self.__config.reference_count_size
            return Utils.read_arb_bitfield(self.__config, ptr, offset)
        if p_type == PropertyType.Int64 or p_type == PropertyType.InstanceID or p_type == PropertyType.Bitfield64:
            offset = self.__config.reference_count_size
            return self.__memory.read_uint(ptr+offset)
        if p_type == PropertyType.TimeStamp:
            offset = self.__config.reference_count_size
            return self.__memory.read_double(ptr+offset)
        if p_type == PropertyType.Vector:
            offset = self.__config.reference_count_size
            x = self.__memory.read_float(ptr+offset)
            y = self.__memory.read_float(ptr+offset+4)
            z = self.__memory.read_float(ptr+offset+8)
            vector_3d = Vector3D(x, y, z)
            return vector_3d
        if p_type == PropertyType.Color:
            offset = self.__config.reference_count_size
            red = int.from_bytes(self.__memory.read_bytes(ptr+offset, 1), "little")
            green = int.from_bytes(self.__memory.read_bytes(ptr+offset+4, 1), "little")
            blue = int.from_bytes(self.__memory.read_bytes(ptr+offset+8, 1), "little")
            alpha = int.from_bytes(self.__memory.read_bytes(ptr+offset+12, 1), "little")
            color = Color(red, green, blue, alpha)
            return color
        if p_type == PropertyType.Position:
            offset = self.__config.reference_count_size
            pad = 6 if self.__config.is_64bits else 2
            start_offset = offset + self.__config.pointer_size
            region = self.__memory.read_uint(ptr+start_offset+0)
            bx = int.from_bytes(self.__memory.read_bytes(ptr+start_offset+4, 1), "little") & 0xFF
            by = int.from_bytes(self.__memory.read_bytes(ptr+start_offset+5, 1), "little") & 0xFF
            cell = self.__memory.read_short(ptr+start_offset+6) & 0xFFFF
            instance = self.__memory.read_short(ptr+start_offset+8) & 0xFFFF
            x = self.__memory.read_float(ptr+start_offset+10+pad)
            y = self.__memory.read_float(ptr+start_offset+14+pad)
            z = self.__memory.read_float(ptr+start_offset+18+pad)
            pos = Vector3D(x, y, z)
            position = Position.make(region, bx, by, instance, cell, pos, None)
            return position            
        return None

    def handle_prop_from_mem(self, ptr: int, offset: int, property_def: PropertyDef) -> object:
        p_type = property_def.ptype.val
        property_val_offset = offset + self.__config.pointer_size
        prop_val = None
        if p_type == PropertyType.Bool:
            prop_val = self.__memory.read_bool(ptr + property_val_offset)
            assert prop_val == 1 or prop_val == 0
        elif p_type in (PropertyType.EnumMapper, PropertyType.Int, PropertyType.PropertyID, PropertyType.Bitfield32, PropertyType.DataFile):
            prop_val = self.__memory.read_uint(ptr + property_val_offset)
        elif p_type == PropertyType.Float:
            prop_val = self.__memory.read_float(ptr + property_val_offset)
        else:
            value_ptr = self.__memory.read_uint(ptr + property_val_offset)
            prop_val = self.handle_pointer_prop_val(value_ptr, property_def)
        return prop_val

    def get_string_from_bit_field(self, bit_field: BitSet, enum_mapper: EnumMapper, seperator: str) -> str:
        length = bit_field.count
        if length > 0:
            result_str = ""
            for i in range(length):
                if bit_field.get(i):
                    item_str = enum_mapper.get_str(i+1)
                    if item_str:
                        if len(result_str) > 0: result_str += seperator
                        result_str += item_str
            return result_str
        return None

    def handle_property(self, ptr: int, offset: int, property_def: PropertyDef) -> PropertyValue:
        if property_def and property_def.pid == 0: return PropertyValue(property_def, None, None)
        property_desc_ptr = self.__memory.read_uint(ptr+offset)
        assert property_desc_ptr is not None
        property_def = self.load_property_descriptor(property_desc_ptr, property_def)
        if property_def is None: return None
        prop_value = self.handle_prop_from_mem(ptr, offset, property_def)
        complement: str = ""
        if isinstance(prop_value, BitSet):
            bit_field: BitSet = prop_value
            enum_id = property_def.data
            enum_mapper = self.__data_facade.get_enums_manager().get_enum_mapper(enum_id)
            complement = self.get_string_from_bit_field(bit_field, enum_mapper, ',')
        if isinstance(prop_value, list):
            return ArrayPropertyValue(property_def, prop_value)
        return PropertyValue(property_def, prop_value, complement)

    def handle_prop_map_entry(self, storage: Properties, hash_table_data_ptr: int) -> None:
        if hash_table_data_ptr is None: return
        property_id = self.__memory.read_uint(hash_table_data_ptr)
        if self.__debug: print('Property ID:', property_id)
        prop_def = self.__data_facade.get_properties_registry().get_property_def(property_id)
        offset = self.__config.map_int_keysize + self.__config.pointer_size
        property_value = self.handle_property(hash_table_data_ptr, offset, prop_def)
        if self.__debug: print(f"{property_value.prop_definition.name}: {property_value.value}")
        if property_value: storage.set_property(property_value)
        next = self.__memory.read_uint(hash_table_data_ptr + self.__config.map_int_keysize)
        if next: 
            self.handle_prop_map_entry(storage, next)

    def handle_properties(self, ptr: int, hash_table_offset: int):
        buckets_ptr = self.__memory.read_uint(ptr+hash_table_offset+(2*self.__config.pointer_size))
        if self.__debug: print(f"buckets_ptr: {hex(buckets_ptr)}")

        first_bucket_ptr = self.__memory.read_uint(ptr+hash_table_offset+(3*self.__config.pointer_size))
        if self.__debug: print(f"first_bucket_ptr: {hex(first_bucket_ptr)}")

        nb_buckets = self.__memory.read_uint(ptr+hash_table_offset+(4*self.__config.pointer_size))
        nb_elements = self.__memory.read_uint(ptr+hash_table_offset+(4*self.__config.pointer_size)+0x4)
        if self.__debug: print(f"Properties: nb_buckets: {nb_buckets}, nb_elements: {nb_elements}")

        storage = Properties()
        if buckets_ptr and nb_elements > 0:
            for i in range(nb_buckets):
                first_entry = self.__memory.read_uint(buckets_ptr+(i*self.__config.pointer_size))
                if first_entry:
                    self.handle_prop_map_entry(storage, first_entry)
        map_size = len(storage.props)
        if map_size != nb_elements:
            print(f'Mismatch: got {map_size} properties but expected {nb_elements}')
        return storage
