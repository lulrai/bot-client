from backend.managers.tags_manager import OptionItem, Tag
from backend.managers.strings_manager import StringTableEntry
from backend.managers.knownvariables_manager import KnownVariablesManager
from backend.strings.string_parser import StringParser, StringPart, VariablePart, LiteralPart

class StringFormatBuilder():
    @staticmethod
    def format(entry: StringTableEntry) -> str:
        try:
            decoded_parts: list[list[StringPart]] = []
            for part in entry.label_strings:
                decoded_part = StringParser.parse(part)
                decoded_parts.append(decoded_part)
            has_var = any(isinstance(part, VariablePart) for parts in decoded_parts for part in parts)
            if has_var:
                return StringFormatBuilder.__render_entry_with_variables(entry, decoded_parts)
            return StringFormatBuilder.__render_entry_without_variables(entry)
        except Exception as e:
            raise e
            print('Could not render string for entry:', entry)
            return '?'

    @staticmethod
    def __render_entry_with_variables(entry: StringTableEntry, decoded_parts: list[list[StringPart]]) -> str:
        variables_index: dict[int, str] = StringFormatBuilder.__build_index(entry, decoded_parts)
        result_str = ''
        for parts in decoded_parts:
            for part in parts:
                if isinstance(part, VariablePart):
                    variable_part: VariablePart = part
                    StringFormatBuilder.__render_variable_part(variables_index, variable_part, result_str)
                elif isinstance(part, LiteralPart):
                    literal_part: LiteralPart = part
                    result_str += literal_part.value
        return result_str

    @staticmethod
    def __render_entry_without_variables(entry: StringTableEntry) -> str:
        variable_ids = entry.variable_ids
        variables_manager = KnownVariablesManager()
        result_str = ''
        parts = entry.label_strings
        result_str += parts[0]
        for i in range(1, len(parts)):
            result_str = result_str.join(['${', variables_manager.get_variable_from_hash(variable_ids[i-1]), '}', parts[i]])
        return result_str

    @staticmethod
    def __build_index(entry: StringTableEntry, decoded_parts: list[list[StringPart]]) -> dict[int, str]:
        map: dict[int, str] = {}
        position = 0
        variable_ids = entry.variable_ids
        variables_manager = KnownVariablesManager()
        for parts in decoded_parts:
            for part in parts:
                if isinstance(part, VariablePart):
                    variable_part: VariablePart = part
                    index = variable_part.index
                    if index not in map:
                        variable_id = variable_ids[position]
                        variable_name = variables_manager.get_variable_from_hash(variable_id)
                        position += 1
                        map[index] = variable_name
        return map

    @staticmethod
    def __render_variable_part(variables_index: dict[int, str], variable_part: VariablePart, output: str) -> None:
        idx = variable_part.index
        variable_name = variables_index.get(idx)
        options = variable_part.options
        if options:
            StringFormatBuilder.__render_options_format(variable_name, options, output)
        else:
            if idx > 0: ouput = output.join(['${', variable_name, '}'])

    @staticmethod
    def __render_options_format(variable_name: str, options: list[OptionItem], output: str) -> None:
        output = output.join(['${', variable_name, ':'])
        for i in range(len(options)):
            text = options[i].text
            if i > 0: output += '|'
            output += text
            tags: list[Tag] = options[i].tags
            if tags:
                output += '['
                for j in range(len(tags)):
                    if j > 0: output += ','
                    output += tags[j].name
                output += ']'
        output += '}'