from __future__ import annotations

import io
import struct
from typing import TYPE_CHECKING

from backend.common.data_types import BitSet
from backend.managers.abstract_mappers import (AbstractMapper, DIDMapper,
                                               EnumMapper)
from backend.managers.properties_manager import PropertiesRegistry
from backend.properties.properties_def import PropertyDef
from backend.properties.properties_set import Properties
from backend.properties.properties_type import PropertyType
from backend.properties.properties_val import ArrayPropertyValue, PropertyValue
from backend.strings.string_info_utils import StringInfoUtils
from backend.utils.common_utils import Utils
from backend.utils.prop_utils import PropertiesUtils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class DBPropertiesLoader():
    def __init__(self, facade: DataFacade) -> None:
        self.__facade: DataFacade = facade

    def decode_properties_resource(self, buffer: bytearray) -> Properties:
        ins: io.BytesIO = io.BytesIO(buffer)
        did = Utils.read_uint32(ins)
        result: Properties = Properties()
        try:
            self.decode_properties(ins, result)
        except Exception:
            print('Could not decode properties ID=', did)
        return result

    def decode_properties(self, ins: io.BytesIO, result: Properties) -> None:
        nb_props = Utils.read_tsize(ins)
        for _ in range(nb_props):
            value: PropertyValue = self.decode_property(ins, True)
            result.set_property(value)

    def decode_property(self, ins: io.BytesIO, double_pid: bool) -> PropertyValue:
        property_id = Utils.read_uint32(ins)
        if property_id == 0: return None
        if double_pid:
            double_property_id = Utils.read_uint32(ins)
            assert double_property_id == property_id
        return self.decode_property_value(ins, property_id)

    def decode_property_value(self, ins: io.BytesIO, property_id: int) -> PropertyValue:
        array_property_val: ArrayPropertyValue = None
        registry: PropertiesRegistry = self.__facade.get_properties_registry()
        definition: PropertyDef = registry.get_property_def(property_id)
        if definition is None: raise Exception('Property definition not found:', property_id)
        type: PropertyType = definition.ptype
        value: object = PropertiesUtils.read_property_value(ins, type)
        result: PropertyValue = None
        complement: object = None
        if type == PropertyType.Array:
            nb_items: int = int(value)
            values: list[PropertyValue] = [None] * nb_items
            for i in range(nb_items):
                values[i] = self.decode_property(ins, False)
            array_property_val = ArrayPropertyValue(definition, values)
            value = values
        elif type == PropertyType.Struct:
            set: Properties = Properties()
            nb_items: int = int(value)
            for _ in range(nb_items):
                set.set_property(self.decode_property(ins, True))
            value = set
        elif type == PropertyType.StringInfo:
            value = StringInfoUtils.build_string_format(self.__facade.get_strings_manager(), value)
        elif type == PropertyType.EnumMapper:
            enum_id = definition.data
            mapper: AbstractMapper = self.__get_enum(enum_id)
            if mapper is not None: complement = mapper.get_label(int(value))
            else: print('WARN: Unsupported enum identifier:', enum_id)
        elif type == PropertyType.PropertyID:
            if isinstance(value, int):
                property_def: PropertyDef = self.__facade.get_properties_registry().get_property_def(int(value))
                if property_def is not None: complement = property_def.name
        elif type == PropertyType.Bitfield32:
            if isinstance(value, int):
                enum_id = definition.data
                enum_mapper: EnumMapper = self.__facade.get_enums_manager().get_enum_mapper(enum_id)
                bitset: BitSet = BitSet.from_flags(int(value))
                complement = bitset.get_string(enum_mapper, ',')
        elif type == PropertyType.Bitfield:
             if isinstance(value, BitSet):
                bitset: BitSet = value
                enum_id = definition.data
                enum_mapper: EnumMapper = self.__facade.get_enums_manager().get_enum_mapper(enum_id)
                complement = bitset.get_string(enum_mapper, ',')
        elif type == PropertyType.Bitfield64:
            if isinstance(value, int):
                enum_id = definition.data
                enum_mapper: EnumMapper = self.__facade.get_enums_manager().get_enum_mapper(enum_id)
                bitset: BitSet = BitSet.from_flags(int(value), True)
                complement = bitset.get_string(enum_mapper, ',')
        if array_property_val is None:
            return PropertyValue(definition, value, complement)
        return None

    def __get_enum(self, enum_id: int) -> AbstractMapper:
        mapper: AbstractMapper = None
        if enum_id >= 587202560 and enum_id <= 603979775: 
            return self.__facade.get_enums_manager().get_enum_mapper(enum_id)
        elif enum_id >= 671088640 and enum_id <= 687865855:
            data: bytearray = self.__facade.load_data(enum_id)
            ins: io.BytesIO = io.BytesIO(data)
            did: int = Utils.read_uint32(ins)
            data_id_map: dict[int, int] = {}
            labels_map: dict[int, str] = {}
            while Utils.bytes_available(ins):
                count = Utils.read_tsize(ins)
                for _ in range(count):
                    key, val = struct.unpack('<2L', ins.read(8))
                    data_id_map[key] = val
                assert count == Utils.read_tsize(ins)
                for _ in range(count):
                    key = Utils.read_uint32(ins)
                    label = Utils.read_ascii_string(ins)
                    labels_map[key] = label
            if Utils.bytes_available(ins): print('WARN: Expected 0 available bytes here. Got:', Utils.bytes_available(ins))
            result: DIDMapper = DIDMapper(did)
            for key in data_id_map:
                id = data_id_map.get(key)
                label = labels_map.get(key)
                if label is not None:
                    result.add(key, id, label)
                    continue
                else: print('WARN: Label not found for key:', key, ' and id:', id)
            return result
        else:
            return None
