from backend.managers.tags_manager import Tag, TagsManager, OptionItem

class StringPart():
    pass

class VariablePart(StringPart):
    def __init__(self, index: int, options: list[OptionItem]) -> None:
        super().__init__()
        self.__index = index
        self.__options = options
    
    @property
    def index(self) -> int:
        return self.__index
    @property
    def options(self) -> list[OptionItem]:
        return self.__options

class LiteralPart(StringPart):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.__value = value
    
    @property
    def value(self) -> str:
        return self.__value

class StringParser():
    SHARP = '#'
    OPEN_BRACE = '{'
    CLOSE_BRACE = '}'
    OPEN_BRACKET = '['
    CLOSE_BRACKET = ']'
    COLON = ':'

    @staticmethod
    def parse(input: str) -> list[StringPart]:
        string_part: list[StringPart] = []
        index = 0
        range = [0] * 2
        while index < len(input):
            variable_part = StringParser.parse_variable_reference(input, index, range)
            if variable_part:
                start_index = range[0]
                if start_index > index:
                    parse_string = input[index:start_index]
                    string_part.append(LiteralPart(parse_string))
                string_part.append(variable_part)
                index = range[1] + 1
                continue
            literal_string = input[index:]
            string_part.append(LiteralPart(literal_string))
            index = len(input)
        return string_part

    @staticmethod
    def parse_variable_reference(input: str, index: int, range: list[int]) -> VariablePart:
        sharp_index = input.find(StringParser.SHARP, index)
        if sharp_index == -1: return None
        colon_index = input.find(StringParser.COLON, sharp_index+1)
        if colon_index == -1: return None
        try:
            number = int(input[sharp_index+1 : colon_index])
        except ValueError:
            return None
        options: list[OptionItem] = None
        end_index = colon_index
        open_brace = input.find(StringParser.OPEN_BRACE, colon_index+1)
        if open_brace != -1:
            close_brace = input.find(StringParser.CLOSE_BRACE, open_brace+1)
            if close_brace != -1:
                end_index = close_brace
            options_str = input[open_brace+1:close_brace]
            options = StringParser.parse_options(options_str)
        range[0] = sharp_index
        range[1] = end_index
        variable_part = VariablePart(number, options)
        return variable_part

    @staticmethod
    def parse_options(options_str: str) -> list[OptionItem]:
        option_items: list[OptionItem] = []
        option_item_strs = options_str.split('|')
        for option_item_str in option_item_strs:
            tags = None
            tag_str = StringParser.extract_tags_str(option_item_str)
            if tag_str is not None:
                tags = StringParser.parse_tags(tag_str)
                open_bracket = option_item_str.find(StringParser.OPEN_BRACKET)
                text = option_item_str[0:open_bracket]
            option_item = OptionItem(text, tags)
            if option_item: option_items.append(option_item)
        return option_items
    
    @staticmethod
    def extract_tags_str(option_item_str: str) -> str:
        open_bracket = option_item_str.find(StringParser.OPEN_BRACKET)
        if open_bracket != -1:
            close_bracket = option_item_str.find(StringParser.CLOSE_BRACKET, open_bracket+1)
            if close_bracket != -1:
                close_bracket = len(option_item_str)-1
            return option_item_str[open_bracket+1:close_bracket]
        return None

    @staticmethod
    def parse_tags(tag_str: str) -> list[Tag]:
        tags: list[Tag] = []
        tags_manager = TagsManager()
        negative = False
        for ch in tag_str:
            if ch != ',':
                if ch == '!':
                    negative = True
                else:
                    tag_definition = tags_manager.get_tag(ch)
                    if tag_definition:
                        tag = Tag(tag_definition, negative)
                        tags.append(tag)
                    negative = False
        return tags