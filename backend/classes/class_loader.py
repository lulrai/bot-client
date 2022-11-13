from __future__ import annotations

import io
import struct
import zlib
from collections import defaultdict
from typing import TYPE_CHECKING, Generic, TypeVar

from backend.classes.class_definition import ClassDefinition
from backend.classes.geo_data import (AchievableGeoData, AchievableGeoDataItem,
                                      DidGeoData, GeoData)
from backend.common.data_types import BitSet, Position
from backend.common.vault_data import VaultDescriptor, VaultItemDescriptor
from backend.managers.strings_manager import StringsManager
from backend.properties.dbprops_loader import DBPropertiesLoader
from backend.properties.properties_set import Properties
from backend.properties.properties_val import PropertyValue
from backend.reference.data_ref import DataIdentification, DataReference
from backend.strings.string_info_utils import StringInfoUtils
from backend.utils.common_utils import Utils
from backend.utils.prop_utils import PropertiesUtils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade


RESULT = TypeVar('RESULT')
class WStateClassLoader(Generic[RESULT]):
    def decode_data(self, ins: io.BytesIO):
        pass


class AAHashLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> dict[int, object]:
        count = Utils.read_tsize(ins)
        result: dict[int, object] = {}
        for _ in range(count):
            key = Utils.read_uint32(ins)
            val = Utils.read_uint32(ins)
            map_val = DataReference(val) if self.__use_ref else val
            result[key] = map_val
        return result


class AAMultiHashLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> dict[int, list[object]]:
        count = Utils.read_tsize(ins)
        result: dict[int, list[object]] = defaultdict(list)
        for _ in range(count):
            key = Utils.read_uint32(ins)
            val = Utils.read_uint32(ins)
            map_val = DataReference(val) if self.__use_ref else val
            result[key].append(map_val)
        return result


class AArrayLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> list[object]:
        arr = Utils.read_prefixed_array(ins, 'L', 'L')
        result: list[object] = []
        for value in arr:
            map_val = DataReference(value) if self.__use_ref else value
            result.append(map_val)
        return result


class AHashSetLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> set[object]:
        count, _ = struct.unpack('<2H', ins.read(4))
        result: set[object] = set()
        for _ in range(count):
            value = Utils.read_uint32(ins)
            result.add(value)
        return result


class ALHashLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> dict[int, int]:
        count = Utils.read_tsize(ins)
        result: dict[int, int] = {}
        for _ in range(count):
            key = Utils.read_uint32(ins)
            val = Utils.read_int64(ins)
            result[key] = val
        return result


class AListLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> list[object]:
        arr = Utils.read_prefixed_array(ins, 'L', 'L')
        result: list[object] = []
        for value in arr:
            map_val = DataReference(value) if self.__use_ref else value
            result.append(map_val)
        return result


class ARHashLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> dict[int, object]:
        count = Utils.read_tsize(ins)
        result: dict[int, object] = {}
        for _ in range(count):
            key = Utils.read_uint32(ins)
            val = Utils.read_int32(ins)
            map_val = DataReference(val) if self.__use_ref else val
            result[key] = map_val
        return result


class ARMultiHashLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> dict[int, list[object]]:
        count = Utils.read_tsize(ins)
        result: dict[int, list[object]] = defaultdict(list)
        for _ in range(count):
            key = Utils.read_uint32(ins)
            val = Utils.read_uint32(ins)
            map_val = DataReference(val) if self.__use_ref else val
            result[key].append(map_val)
        return result


class LAHashLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> dict[int, int]:
        count = Utils.read_tsize(ins)
        result: dict[int, int] = {}
        for _ in range(count):
            key = Utils.read_int64(ins)
            val = Utils.read_uint32(ins)
            result[key] = val
        return result


class LArrayLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[int]:
        count = Utils.read_uint32(ins)
        return [struct.unpack('<q', ins.read(8))[0]
                      for _ in range(count)]


class LHashSetLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[int]:
        count, _ = struct.unpack('<2H', ins.read(4))
        return [struct.unpack('<q', ins.read(8))[0]
                      for _ in range(count)]


class LListLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[int]:
        return list(Utils.read_prefixed_array(ins, 'L', 'L'))


class LRHashLoader(WStateClassLoader):
    def __init__(self, use_ref: bool = False) -> None:
        super().__init__()
        self.__use_ref = use_ref

    def decode_data(self, ins: io.BytesIO) -> dict[int, object]:
        count = Utils.read_tsize(ins)
        result: dict[int, object] = {}
        for _ in range(count):
            key = Utils.read_uint64(ins)
            val = Utils.read_uint32(ins)
            map_val = DataReference(val) if self.__use_ref else val
            result[key] = map_val
        return result


class NAHashLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[list[object]]:
        count = Utils.read_tsize(ins)
        result: list[list[object]] = list()
        for _ in range(count):
            v1 = Utils.read_uint32(ins)
            v2 = Utils.read_uint32(ins)
            v4 = Utils.read_uint32(ins)
            item: list[object] = []
            item.append(DataReference(v1))
            item.append(v2)
            item.append(DataReference(v4))
            result.append(item)
        return result


class NHashSetLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> str:
        count, _ = struct.unpack('<2H', ins.read(4))
        _ = [struct.unpack('<LLB', ins.read(9))
                      for _ in range(count)]
        return 'NHashSet: size='+count


class NRHashLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[list[object]]:
        count = Utils.read_tsize(ins)
        result: list[list[object]] = list()
        for _ in range(count):
            v1 = Utils.read_uint32(ins)
            v2 = Utils.read_uint32(ins)
            v4 = Utils.read_uint32(ins)
            item: list[object] = []
            item.append(DataReference(v1))
            item.append(v2)
            item.append(DataReference(v4))
            result.append(item)
        return result


class RArrayLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[int]:
        return list(Utils.read_prefixed_array(ins, 'L', 'l'))


class RListLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> list[int]:
        return list(Utils.read_prefixed_array(ins, 'L', 'l'))

class BasePropertyLoader(WStateClassLoader):
    def __init__(self, facade: DataFacade) -> None:
        super().__init__()
        self.__facade = facade

    def decode_data(self, ins: io.BytesIO) -> PropertyValue:
        loader: DBPropertiesLoader = DBPropertiesLoader(self.__facade)
        return loader.decode_property(ins, True)

class DynamicBitsetLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> BitSet:
        return BitSet.from_stream(ins)

class PositionLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> Position:
        return Position.from_dat(ins)

class PropertiesLoader(WStateClassLoader):
    def __init__(self, facade: DataFacade) -> None:
        super().__init__()
        self.__facade = facade

    def decode_data(self, ins: io.BytesIO) -> Properties:
        result: Properties = Properties()
        loader: DBPropertiesLoader = DBPropertiesLoader(self.__facade)
        loader.decode_properties(ins, result)
        return result

class RandomSelectionTableLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> dict[int, int]:
        count = Utils.read_uint32(ins)
        result: dict[int, int] = {}
        for _ in range(count):
            val = Utils.read_uint32(ins)
            weight = Utils.read_uint32(ins)
            _ = Utils.read_uint32(ins)
            result[val] = weight
        assert Utils.read_uint32(ins) == 0
        return result

class StringInfoLoader(WStateClassLoader):
    def __init__(self, facade: DataFacade) -> None:
        super().__init__()
        self.__facade = facade

    def decode_data(self, ins: io.BytesIO) -> str:
        str_info = PropertiesUtils.read_string_info(ins)
        str_manager: StringsManager = self.__facade.get_strings_manager()
        return StringInfoUtils.render_string_info(str_manager, str_info)

class StringLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> str:
        return Utils.read_prefixed_utf16(ins)

class DiscoveredMapNoteDataLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> BitSet:
        buffer_size = Utils.read_uint32(ins)
        buffer: bytearray = bytearray(ins.read(buffer_size))
        ins_new: io.BytesIO = io.BytesIO(buffer)
        assert Utils.read_uint32(ins_new) == 0
        unpacked_size = Utils.read_uint32(ins_new)
        packed_size = ins_new.getbuffer().nbytes
        buffer: bytearray = bytearray(ins_new.read(packed_size))
        mv = memoryview(buffer)
        decompressed_buffer = bytearray(zlib.decompress(mv,
                                   zlib.Z_DEFAULT_STRATEGY,
                                   packed_size))
        assert len(decompressed_buffer) == unpacked_size
        nb_bits = packed_size * 8
        return BitSet.from_stream(ins, nb_bits)

class GameplayOptionsProfileLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> None:
        _, _, num_sets = struct.unpack('<LLL', ins.read(12))
        for i in range(num_sets):
            assert Utils.read_uint32(ins) == 84
            print(f'Set #{i}')
            for j in range(7):
                print(f'\t Bar #{j}')
                for k in range(12):
                    print(f'\t\t Slot #{k}')
                    shortcut_type = Utils.read_uint32(ins)
                    if shortcut_type == 0: print('\t\t\t Nothing!')
                    elif shortcut_type == 2:
                        iid, did = struct.unpack('<qL', ins.read(12))
                        print(f'\t\t\t Item: IID={iid}, DID={did}!')
                    elif shortcut_type == 6: print(f'\t\t\t Skill: DID={Utils.read_uint32(ins)}')
                    elif shortcut_type == 7: print(f'\t\t\t Pet: DID={Utils.read_uint32(ins)}') 
                    elif shortcut_type == 9: print(f'\t\t\t Hobby: DID={Utils.read_uint32(ins)}') 
                    else: raise Exception('Illegal new type!')
        test1, test2 = struct.unpack('<BB', ins.read(2))
        if test1 in (0, 1):
            if test2 == 2:
                ins.read(24)
            else:
                for j in range(test2):
                    _, _, elem_cnt = struct.unpack('<LBB', ins.read(6))
                    for _ in range(elem_cnt):
                        _, _, _, _, _, _ = struct.unpack('<L4fB', ins.read(21))
                _ = Utils.read_uint16(ins)
                for k in range(6):
                    _ = Utils.read_uint32(ins)
        
class QuestEventTargetLocationLoader(WStateClassLoader):
    def __init__(self, facade: DataFacade) -> None:
        super().__init__()
        self.__facade: DataFacade = facade
        self.__data_id_cache: dict[int, DataIdentification] = {}
        __wclass = ClassDefinition(0, '')
        __data_id0 = DataIdentification(0, '', __wclass)
        self.__data_id_cache[__data_id0.did] = __data_id0

    def decode_data(self, ins: io.BytesIO) -> GeoData:
        data: GeoData = GeoData()
        # Read Position map
        count = Utils.read_tsize(ins)
        for _ in range(count):
            did, num_positions = struct.unpack('<2L', ins.read(8))
            if num_positions > 0:
                geo: DidGeoData = DidGeoData(did)
                for _ in range(num_positions):
                    position: Position = Position.from_dat(ins)
                    if position.instance != 0: print('I is not 0!')
                    geo.add_geo_data(position)
                    a = Utils.read_uint32(ins)
                    if a != 0: print('A is not 0!')
                    b = Utils.read_uint8(ins)
                    if b not in (0, 1): print('B is not 0 or 1!')
                data.add_world_geodata(geo)
        # Decode Genus Map
        assert Utils.read_uint32(ins) == 7
        for _ in range(7):
            nb_arrays = Utils.read_tsize(ins)
            for _ in range(nb_arrays):
                _ = Utils.read_uint32(ins)
                _ = list(Utils.read_prefixed_array(ins, 'L', 'L'))
        # Decode Content Layer Position Map
        self.__decode_content_layer_position_map(data, ins)
        # Decode Quest Entries
        self.__decode_quest_entries(data, ins)
        return data

    def __decode_content_layer_position_map(self, data: GeoData, ins: io.BytesIO) -> None:
        count = Utils.read_tsize(ins)
        for _ in range(count):
            did, num_positions = struct.unpack('<2L', ins.read(8))
            if num_positions > 0:
                content_layer_positions: dict[int, list[Position]] = {}
                for _ in range(num_positions):
                    position: Position = Position.from_dat(ins)
                    if position.instance != 0: print('I is not 0!')
                    a = Utils.read_uint32(ins)
                    if a != 0: print('A is not 0!')
                    b = Utils.read_uint8(ins)
                    if b != 0 and b != 1: print('B is not 0 or 1!')
                    layers: list[int] = list(Utils.read_prefixed_array(ins, 'L', 'L'))
                    for layer in layers:
                        positions: list[Position] = content_layer_positions.get(layer)
                        if positions is None:
                            positions = []
                            content_layer_positions[layer] = positions
                        positions.append(position)
                for content_layer in content_layer_positions.keys():
                    geo: DidGeoData = DidGeoData(did)
                    for position in content_layer_positions.get(content_layer):
                        geo.add_geo_data(position)
                    layer_id = content_layer
                    if layer_id == 0: print('Found CL 0!')
                    data.add_content_layer_geodata(geo, layer_id)
    

    def __decode_quest_entries(self, data: GeoData, ins: io.BytesIO) -> None:
        count = Utils.read_tsize(ins)
        for _ in range(count):
            quest_id = Utils.read_uint32(ins)
            print('Quest ID:', quest_id)
            geo_data: AchievableGeoData = AchievableGeoData(quest_id)
            nb_objectives = Utils.read_tsize(ins)
            for _ in range(nb_objectives):
                objective_index = Utils.read_uint32(ins)
                print('\t Objective #:', objective_index)
                conditions_count = Utils.read_uint32(ins)
                for condition_idx in range(conditions_count):
                    print('\t\t Condition #:', condition_idx)
                    entries_count = Utils.read_uint32(ins)
                    for entry_idx in range(entries_count):
                        print('\t\t\t Entry #:', entry_idx)
                        item: AchievableGeoDataItem = self.__read_quest_entry(quest_id, ins)
                        if item: geo_data.add_geodata(objective_index, condition_idx, item)
            if not geo_data.empty:
                data.add_geodata(geo_data)

    def __read_quest_entry(self, quest_id: int, ins: io.BytesIO) -> AchievableGeoDataItem:
        did = Utils.read_uint32(ins)
        position: Position = Position.from_dat(ins)
        radius = Utils.read_float(ins)
        str1 = Utils.read_pascal_string(ins)
        if len(str1) > 0 and did > 0:
            did_id: DataIdentification = self.__identify(did)
            print('DID found for string 1:', did_id)
        count = Utils.read_uint32(ins)
        if count > 0:
            for _ in range(count):
                self.__read_quest_genus_struct(ins)
        str2 = Utils.read_pascal_string(ins)
        if len(str2) > 0:
            if did > 0:
                did_id: DataIdentification = self.__identify(did)
                if did_id.wClass_name != 'IItem': print('DID is not an item! ->', did_id)
                elif len(str1) == 0: print('Found str2 with no str1 and no DID! s2=:', str2)
        result: AchievableGeoDataItem = None
        if position is not None:
            result = AchievableGeoDataItem(str1, str2, did, position)
        return result

    def __read_quest_genus_struct(self, ins: io.BytesIO) -> None:
        flags = ord(ins.read(1))
        if flags & 0x01: m_eGenusType, = struct.unpack('<L', ins.read(4))
        if flags & 0x02: m_eSpeciesType, = struct.unpack('<L', ins.read(4))
        if flags & 0x04: m_eSubspeciesType, = struct.unpack('<L', ins.read(4))
        if flags & 0x08: m_eAlignmentType, = struct.unpack('<L', ins.read(4))
        if flags & 0x10: m_eClassType, = struct.unpack('<L', ins.read(4))
        if flags & 0x20: m_eMonsterDivision, = struct.unpack('<L', ins.read(4))
        if flags & 0x40: m_didLandmark, = struct.unpack('<L', ins.read(4))

    def __identify(self, did: int) -> DataIdentification:
        data_id = self.__data_id_cache.get(did)
        if data_id is None:
            wclass: ClassDefinition = None
            data: bytearray = self.__facade.load_data(did)
            temp_ins: io.BytesIO = io.BytesIO(data)
            if data:
                _, class_def_idx = struct.unpack('<2L', temp_ins.read(8))
                wclass = self.__facade.get_wlib_data().get_class(class_def_idx)
            else: print('Cannot load data:', did)
            props = self.__facade.load_properties(did + 150994944)
            if props is not None:
                name = Utils.get_string_property(props, 'Name')
                if name is None:
                    name = Utils.get_string_property(props, 'Area_Name')
            if name is not None:
                name_fix_idx = name.rfind('[')
                if name_fix_idx != -1: name = name[0:name_fix_idx]
            else:
                name = '?'
            data_id = DataIdentification(did, name, wclass)
            self.__data_id_cache[data_id.did] = data_id
        return data_id
        
class BankRepositoryDataAdaptorLoader(WStateClassLoader):
    def __init__(self, props_loader: PropertiesLoader, base_props_loader: BasePropertyLoader) -> None:
        super().__init__()
        self.__props_loader = props_loader
        self.__base_props_loader = base_props_loader

    def decode_data(self, ins: io.BytesIO) -> VaultItemDescriptor:
        item_IID: int = Utils.read_uint64(ins)
        props: Properties = self.__props_loader.decode_data(ins)
        tooltip_helper_info: PropertyValue = self.__base_props_loader.decode_data(ins)
        return VaultItemDescriptor(item_IID, props, tooltip_helper_info)

class BankRepositoryDataLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> VaultDescriptor:
        result: VaultDescriptor = VaultDescriptor()
        size = Utils.read_tsize(ins)
        for _ in range(size):
            chest_id = Utils.read_uint32(ins)
            chest_name = Utils.read_prefixed_utf16(ins)
            result.add_chest(chest_id, chest_name)
        total_capacity, current_quantity = struct.unpack('<2L', ins.read(8))
        result.set_state(current_quantity, total_capacity)
        return result

class GenericLoader(WStateClassLoader):
    def __init__(self, code: str) -> None:
        super().__init__()
        self.__code: str = code

    def decode_data(self, ins: io.BytesIO) -> list[int]:
        size = struct.calcsize(self.__code)
        return list(struct.unpack('<{}'.format(self.__code), ins.read(size)))

class BankTypeLoader(WStateClassLoader):
    def decode_data(self, ins: io.BytesIO) -> int:
        return Utils.read_uint32(ins)