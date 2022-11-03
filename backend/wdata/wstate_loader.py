from __future__ import annotations

from typing import TYPE_CHECKING

from backend.classes.class_definition import AttributeDefinition, ClassInstance
from backend.classes.class_loader import *
from backend.wdata.wlib_data import WLibData
from backend.wdata.wstate import WStateDataSet

if TYPE_CHECKING:
    from backend.data_facade import DataFacade


class WStateLoader():
    def __init__(self, facade: DataFacade, wlib_data: WLibData) -> None:
        self.__facade: DataFacade = facade
        self.__wlib_data = wlib_data

    def __get_loader_for_class(self, class_index: int) -> WStateClassLoader:
        if class_index in (11, 35): return AAHashLoader(class_index==35)
        if class_index in (13, 37): return AAMultiHashLoader(class_index==37)
        if class_index in (17, 25, 176, 182): return AAMultiHashLoader(class_index in (176, 182))
        if class_index == 18: return AHashSetLoader()
        if class_index == 23: return ALHashLoader()
        if class_index == 39: return BasePropertyLoader(self.__facade)
        if class_index == 57: return DynamicBitsetLoader()
        if class_index == 104: return LArrayLoader()
        if class_index == 105: return LHashSetLoader()
        if class_index in (117, 97): return LRHashLoader(class_index==117)
        if class_index == 134: return NHashSetLoader()
        if class_index == 138: return NRHashLoader()
        if class_index in (160, 161): return PositionLoader()
        if class_index == 166: return PropertiesLoader(self.__facade)
        if class_index == 175: return RandomSelectionTableLoader()
        if class_index == 199: return StringInfoLoader(self.__facade)
        if class_index == 225: return StringLoader()
        if class_index == 407: return DiscoveredMapNoteDataLoader()
        if class_index == 415: return GameplayOptionsProfileLoader()
        if class_index == 2479: return QuestEventTargetLocationLoader(self.__facade)
        if class_index == 2567:
            prop_loader: PropertiesLoader = PropertiesLoader(self.__facade)
            base_props_loader: BasePropertyLoader = BasePropertyLoader(self.__facade)
            return BankRepositoryDataAdaptorLoader(prop_loader, base_props_loader)
        if class_index == 3103: return BankRepositoryDataLoader()
        if class_index == 3461: return GenericLoader("LLL")
        if class_index == 3740: return BankTypeLoader()
        return None

    def decode_wstate(self, buffer: bytearray) -> WStateDataSet:
        ins: io.BytesIO = io.BytesIO(buffer)
        idx, class_def_idx = struct.unpack('<2L', ins.read(8))
        result: WStateDataSet = WStateDataSet()
        self.__read_imports(ins)
        always_0_v1 = Utils.read_vle(ins)
        always_0_v2 = Utils.read_vle(ins)
        unknown_bool = Utils.read_bool(ins)
        class_chunk_sz = Utils.read_uint32(ins)
        if class_chunk_sz > 0: self.__read_class_bundle(bytearray(ins.read(class_chunk_sz)), result)
        links_present = Utils.read_bool(ins)
        if links_present: self.__read_links(ins)
        last_pids_present = Utils.read_bool(ins)
        if last_pids_present:
            count = Utils.read_tsize(ins)
            for _ in range(count):
                property_id, property_id2 = struct.unpack('<2L', ins.read(8))
                assert property_id == property_id2
        available = Utils.bytes_available(ins)
        if available:
            print('Extra bytes at the end of this WState:', available)
            size = min(available, 1000)
            print(ins.read(size))
        return result

    def __read_links(self, ins: io.BytesIO) -> None:
        count = Utils.read_uint32(ins)
        for _ in range(count):
            bool_val, v1, v2, v3 = struct.unpack('<B3L', ins.read(13))
            props_count = Utils.read_tsize(ins)
            for _ in range(props_count):
                property_id, property_id2 = struct.unpack('<2L', ins.read(8))
                assert property_id == property_id2
            ins.read(1)

    def __read_imports(self, ins: io.BytesIO) -> None:
        count = Utils.read_tsize(ins)
        for _ in range(count):
            dbo_type, did = struct.unpack('<2L', ins.read(8))
            c =  Utils.read_uint8(ins)
            if dbo_type == 69:
                did_highbits = did >> 24
                if did_highbits not in (112, 118): print('WState DID invalid. DID=',did)
                if c not in (0, 16): print('Invalid value of c:', c, 'expected 0 or 16.')
            elif dbo_type == 78:
                did_highbits = did >> 24
                if did_highbits != 32: print('Appearance DID invalid. DID=',did)
                if c != 0: print('Invalid value of c:', c, 'expected 0.')
            else:
                raise Exception('Unhandled DBO type:', dbo_type, 'in DID:', did)

    def __read_class_bundle(self, buffer: bytearray, result: WStateDataSet) -> None:
        ins: io.BytesIO = io.BytesIO(buffer)
        refs_count = Utils.read_vle(ins)
        for _ in range(refs_count):
            reference = Utils.read_uint32(ins)
            result.add_reference(reference)
        class_def_count = Utils.read_uint16(ins)
        for _ in range(class_def_count):
            class_idx, attributes_count = struct.unpack('<2H', ins.read(4))
            for _ in range(attributes_count):
                name_hash = Utils.read_uint32(ins)
                name: str = self.__wlib_data.get_label(name_hash)
                if name is None: name = name_hash
                value_type: int = Utils.read_uint8(ins)
        for _ in range(refs_count):
            value = self.__read_data_item(ins)
            result.add_value(value)
        available = Utils.bytes_available(ins)
        if available > 0:
            print('End of WSL data. Available bytes:', available)
            remaining = ins.read(available)
            print(remaining)
        
    def __read_data_item(self, ins: io.BytesIO) -> object:
        available = Utils.bytes_available(ins)
        if available < 4: raise Exception('Cannot read a marker. Available bytes=', available)
        marker = Utils.read_uint32(ins)
        if marker == 134217728: return Utils.read_uint64(ins)
        if marker == 536870912: return Utils.read_uint32(ins)
        if marker in (0, 268435456): return self.__read_embedded_data(ins)
        raise Exception('Unmanaged marker value:', marker)

    def __read_embedded_data(self, ins: io.BytesIO) -> object:
        class_idx = Utils.read_uint16(ins)
        class_def = self.__wlib_data.get_class(class_idx)
        if class_def is not None:
            result: ClassInstance = ClassInstance(class_def)
            attributes: list[AttributeDefinition] = class_def.attributes
            for attribute in attributes:
                type: int = attribute.type
                if type == 1: value = Utils.read_uint32(ins)
                elif type == 2: value = Utils.read_uint32(ins)
                elif type == 3: value = Utils.read_float(ins)
                elif type in (130, 131, 195):
                    v1, v2 = struct.unpack('<2L', ins.read(8))
                    value = (v2 << 32) + v1
                else: value = None
                result.set_attr_val(attribute, value)
            return result
        else:
            result: object = None
            wstate_class_loader: WStateClassLoader = self.__get_loader_for_class(class_idx)
            if wstate_class_loader is not None:
                try:
                    result = wstate_class_loader.decode_data(ins)
                except Exception:
                    raise Exception('Caught exception when reading an attribute. Class idx:', class_idx)
            else:
                available = Utils.bytes_available(ins)
                size = min(available, 1000)
                print(ins.read(size))
                raise Exception('No wstate class loader found for class idx:', class_idx)
            return result