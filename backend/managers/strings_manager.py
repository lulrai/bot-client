from __future__ import annotations

import io
from typing import TYPE_CHECKING

from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class StringTableEntry():
    def __init__(self, label_parts: list[str], variable_ids: list[int], variable_names: list[str]) -> None:
        self.__label_parts = label_parts
        self.__variable_ids = variable_ids
        self.__variable_names = variable_names

    @property
    def label_strings(self) -> list[str]:
        return self.__label_parts
    @property
    def variable_ids(self) -> list[int]:
        return self.__variable_ids
    @property
    def variable_names(self) -> list[str]:
        return self.__variable_names

class StringTable():
    def __init__(self, data_id: int) -> None:
        self.__data_id = data_id
        self.__entries: dict[int, StringTableEntry] = {}

    @property
    def data_id(self) -> int:
        return self.__data_id
    
    def get_tokens(self) -> list[int]:
        tokens = list(self.__entries.keys())
        tokens.sort()
        return tokens

    def add_entry(self, token: int, entry: StringTableEntry) -> None:
        self.__entries[token] = entry

    def get_string(self, token: int) -> list[str]:
        entry = self.get_entry(token)
        if entry is not None: return entry.label_strings
        return None

    def get_entry(self, token: int) -> StringTableEntry:
        return self.__entries[token]

class StringsManager():
    def __init__(self, facade: DataFacade) -> None:
        self.__facade = facade
        self.__data: dict[int, StringTable] = {}

    def get_entry(self, table_id: int, token_id: int) -> StringTableEntry:
        table = self.__data.get(table_id)
        if not table:
            data = self.__facade.load_data(table_id)
            if data:
                table = self.__decode_string_table_resource(data)
                self.__data[table_id] = table
                return table.get_entry(token_id)
        return None

    def __decode_string_table_resource(self, buffer: bytearray) -> StringTable:
        ins = io.BytesIO(buffer)
        did = Utils.read_uint32(ins)
        str_table = StringTable(did)
        unknown = Utils.read_uint32(ins)
        assert unknown == 1 or unknown == 0
        nb_entries = Utils.read_tsize(ins)
        for _ in range(nb_entries):
            self.__decode_string_sublist(ins, str_table)
        return str_table

    def __decode_string_sublist(self, ins: io.BytesIO, str_table: StringTable) -> None:
        token = Utils.read_uint32(ins)
        unknown = Utils.read_uint32(ins)
        assert unknown == 0
        
        label_parts_count = Utils.read_uint32(ins)
        label_parts: list[str] = []
        for _ in range(label_parts_count):
            label_parts.append(Utils.read_prefixed_utf16(ins))
        nb_variables = Utils.read_uint32(ins)
        variable_ids: list[int] = []
        for _ in range(nb_variables):
            variable_ids.append(Utils.read_uint32(ins))
        assert nb_variables == (label_parts_count - 1)
        
        variable_names: list[str] = []
        has_variable_names = Utils.read_bool(ins)
        if has_variable_names:
            variable_names_cnt = Utils.read_uint32(ins)
            assert variable_names_cnt == nb_variables
            for _ in range(variable_names_cnt):
                variable_names.append(Utils.read_prefixed_utf16(ins))
        entry = StringTableEntry(label_parts, variable_ids, variable_names)
        str_table.add_entry(token, entry)
