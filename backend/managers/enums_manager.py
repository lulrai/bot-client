from __future__ import annotations

import io
from typing import TYPE_CHECKING

from backend.managers.abstract_mappers import EnumMapper
from backend.managers.strings_manager import StringsManager
from backend.strings.string_info_utils import StringInfoUtils
from backend.utils.common_utils import Utils
from backend.utils.prop_utils import PropertiesUtils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class EnumManager():
    def __init__(self, facade: DataFacade) -> None:
        self.__facade = facade
        self.__data: dict[int, EnumMapper] = {}

    def resolve_enum(self, data_id: int, token: int) -> str:
        table = self.get_enum_mapper(data_id)
        if table:
            return table.get_str(token)
        return None

    def get_enum_mapper(self, data_id: int) -> EnumMapper:
        table = self.__data.get(data_id)
        if table is None:
            data: bytearray = self.__facade.load_data(data_id)
            if data:
                strings_manager = self.__facade.get_strings_manager()
                table = self.__decode_enum_mapper_resource(strings_manager, data)
                self.__data[data_id] = table
                base_data_id = table.base_data_id
                if base_data_id:
                    base_enum = self.get_enum_mapper(base_data_id)
                    if base_enum:
                        for token in base_enum.get_tokens():
                            table.add_enum(token, base_enum.get_str(token))
        return table

    def __decode_enum_mapper_resource(self, strings_manager: StringsManager, data: bytearray) -> EnumMapper:
        ins = io.BytesIO(data)
        did = Utils.read_uint32(ins)
        enum_mapper = EnumMapper(did)
        base_did = Utils.read_uint32(ins)
        if base_did: enum_mapper.base_data_id = base_did
        nb_raw_entries = Utils.read_tsize(ins)
        for i in range(nb_raw_entries):
            key = Utils.read_uint32(ins)
            value = Utils.read_pascal_string(ins)
            enum_mapper.add_enum(key, value)
        nb_string_info_entries = Utils.read_tsize(ins)
        for j in range(nb_string_info_entries):
            key = Utils.read_uint32(ins)
            string_info_value = PropertiesUtils.read_string_info(ins)
            value = StringInfoUtils.build_string_format(strings_manager, string_info_value)
            if value: enum_mapper.add_enum(key, value)
        return enum_mapper
    