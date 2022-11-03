from __future__ import annotations

from backend.managers.tags_manager import OptionItem
from backend.strings.string_parser import StringParser

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.strings.string_info_utils import VariableValueProvider

class StringRenderer():
    def __init__(self, provider: VariableValueProvider) -> None:
        self.__provider = provider
        self.__open_variable = "${"
        self.__end_variable = "}"

    def render(self, format: str) -> str:
        result_str = ""
        index = 0
        while(True):
            variable_start_index = format.find(self.__open_variable, index)
            if variable_start_index == -1: return format[index:len(format)]
            result_str += format[index:variable_start_index]
            variable_end_index = format.find(self.__end_variable, index+len(self.__open_variable))
            if variable_end_index != -1:
                variable_part = format[variable_start_index+len(self.__open_variable): variable_end_index]
                self.__render_variable(result_str, variable_part)
                index = variable_end_index + len(self.__end_variable)
                continue

    def __render_variable(self, result_str: str, variable_part: str) -> None:
        index = variable_part.find(':')
        if index == -1:
            str1 = variable_part
            str2 = self.__provider.get_variable(str1)
            result_str += str2
            return
        variable_name = variable_part[0, index]
        value = self.__provider.get_variable(variable_name)
        options_str = variable_part[index+1:]
        options = StringParser.parse_options(options_str)
        option: OptionItem = self.__choose_option(options, value)
        if option: result_str += option.text

    def __choose_option(self, options: list[OptionItem], value: str) -> OptionItem:
        tags_str = StringParser.extract_tags_str(value)
        max = 0
        chosen = None
        default_option = None
        for option in options:
            nb_matches = self.__count_common_tags(option, value, tags_str)
            if nb_matches >= max:
                chosen = option
                max = nb_matches
            tags = option.tags
            if tags is None: default_option = option
        if max == 0:
            chosen = default_option
        return chosen

    def __count_common_tags(self, option: OptionItem, value: str, tags_str: str) -> int:
        tags = option.tags
        if tags is None: return 0
        nb_matches = 0
        for tag in tags:
            char_code = tag.tag_definition.code
            if char_code == 'E':
                if len(value) > 0:
                    nb_matches += 1
            else:
                tag_index = tags_str.find(char_code) if (tags_str is not None) else -1
                if tag.is_negative:
                    if tag_index == -1:
                        nb_matches += 1
                elif tag_index != -1:
                    nb_matches += 1
        return nb_matches