from __future__ import annotations

import numbers
from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.managers.strings_manager import StringsManager
from backend.strings.string_format_builder import StringFormatBuilder
from backend.strings.string_info import (LiteralStringInfo, StringInfo,
                                         TableEntryStringInfo)
from backend.strings.string_renderer import StringRenderer
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class VariableValueProvider():
    def __init__(self, variables_map: dict[str, str]) -> None:
        self.__variables_map = variables_map

    def get_variable(self, variable_name: str) -> str:
        value = self.__variables_map[variable_name]
        if value: return value
        return variable_name

class StringInfoUtils():
    @staticmethod
    def get_string_info_size(config: GameConfig) -> int:
        hash_table_size = 4 * config.pointer_size + 8
        pointer_size = config.pointer_size
        override_size = 8 if config.is_64bits else 4
        return pointer_size + 8 + hash_table_size + pointer_size + override_size + pointer_size + pointer_size

    @staticmethod
    def render_string(format: str, variables_map: dict[str, str]) -> str:
        provider = VariableValueProvider(variables_map)
        renderer = StringRenderer(provider)
        return renderer.render(format)

    @staticmethod
    def build_variables_map(strings_manager: StringsManager, values: dict[str, object]) -> dict[str, str]:
        return_map = dict[str, str]
        if values:
            for entry in values:
                variable_name = entry
                value = values[entry]
                if isinstance(value, StringInfo):
                    string_info: StringInfo = value
                    string_value = StringInfoUtils.render_string_info(strings_manager, string_info)
                elif isinstance(value, numbers.Number):
                    string_value = str(value)
                return_map[variable_name] = string_value
        return return_map

    @staticmethod
    def build_string_format(strings_manager: StringsManager, string_info: StringInfo) -> str:
        if isinstance(string_info, LiteralStringInfo): 
            literal_string_info: LiteralStringInfo = string_info
            return literal_string_info.literal
        if isinstance(string_info, TableEntryStringInfo):
            table_entry_str_info: TableEntryStringInfo = string_info
            table_id = table_entry_str_info.table_id
            token_id = table_entry_str_info.token_id
            entry = strings_manager.get_entry(table_id, token_id)
            if entry is None: return None
            return StringFormatBuilder.format(entry)
        return None     

    @staticmethod
    def render_string_info(strings_manager: StringsManager, string_info: StringInfo) -> str:   
        format: str = StringInfoUtils.build_string_format(strings_manager, string_info)
        if format and isinstance(string_info, TableEntryStringInfo):
            table_entry_string_info: TableEntryStringInfo = string_info
            variables_map = StringInfoUtils.build_variables_map(strings_manager, table_entry_string_info.variables_map)
            str_ret = ""
            if format.find('${') != -1:
                str_ret = StringInfoUtils.render_string(format, variables_map)
            else:
                str_ret = format
            return str_ret
        return format

    @staticmethod
    def handle_literal_str_value(config: GameConfig, string_ptr: int) -> str:
        header_ptr = string_ptr - 12
        str_size = config.mem.read_uint(header_ptr+8)-1
        if str_size == 0: return ""
        string_buffer: bytearray = bytearray(config.mem.read_bytes(string_ptr, str_size*2))
        for i in range(str_size):
            temp = string_buffer[i * 2 + 1]
            string_buffer[i * 2 + 1] = string_buffer[i * 2]
            string_buffer[i * 2] = temp
        string_val = string_buffer.replace(b'\x00', b'').decode("utf-8")
        return string_val

    @staticmethod
    def read_string_info(config: GameConfig, data_facade: DataFacade, value_addr: int, offset: int) -> str:
        hash_table_size = 4 * config.pointer_size + 8
        is_literal_offset = offset + config.pointer_size + 8 + hash_table_size + config.pointer_size
        is_literal = config.mem.read_bool(value_addr+is_literal_offset)
        if is_literal:
            string_ptr = Utils.get_pointer(config.mem, value_addr + offset + config.pointer_size + 8 + hash_table_size, config.pointer_size)
            return StringInfoUtils.handle_literal_str_value(config, string_ptr)
        else:
            token_id = config.mem.read_uint(value_addr + offset + config.pointer_size)
            table_id = config.mem.read_uint(value_addr + offset + config.pointer_size + 4)
            strings_manager = data_facade.get_strings_manager()
            string_info = TableEntryStringInfo(table_id, token_id)
            return StringInfoUtils.render_string_info(strings_manager, string_info)
