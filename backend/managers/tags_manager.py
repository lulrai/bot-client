class TagDefinition():
    def __init__(self, code: str, meaning: str) -> None:
        self.__code = code
        self.__meaning = meaning

    @property
    def code(self) -> str:
        return self.__code
    @property
    def meaning(self) -> str:
        return self.__meaning

class Tag():
    def __init__(self, tag_definition: TagDefinition, negative: bool) -> None:
        self.__tag_defn = tag_definition
        self.__negative = negative
    
    @property
    def tag_definition(self) -> TagDefinition:
        return self.__tag_defn
    @property
    def is_negative(self) -> bool:
        return self.__negative
    @property
    def name(self) -> str:
        return '!'+str(self.__tag_defn.code) if self.__negative else str(self.__tag_defn.code) 

class OptionItem():
    def __init__(self, text: str, tags: list[Tag]) -> None:
        self.__text = text
        self.__tags = tags
    
    @property
    def text(self) -> str:
        return self.__text
    @property
    def tags(self) -> list[Tag]:
        return self.__tags

class TagsManager():
    def __init__(self) -> None:
        self.__tags: dict[str, TagDefinition] = {}
        self.__load_tags()

    def get_tag(self, code: str) -> TagDefinition:
        return self.__tags[code]

    def __register_tag(self, code: str, meaning: str) -> None:
        tag_definition = TagDefinition(code, meaning)
        self.__tags[code] = tag_definition

    def __load_tags(self) -> None:
        self.__register_tag('1', "singular entity")
        self.__register_tag('b', "blank?")
        self.__register_tag('B', "beorning")
        self.__register_tag('C', "captain")
        self.__register_tag('D', "dwarf or stout-axe")
        self.__register_tag('E', "empty")
        self.__register_tag('f', "feminine")
        self.__register_tag('F', "feminine")
        self.__register_tag('G', "burglar")
        self.__register_tag('H', "champion")
        self.__register_tag('I', "minstrel OR thing / neuter")
        self.__register_tag('K', "rune-keeper")
        self.__register_tag('L', "lore-master OR elf or high elf")
        self.__register_tag('m', "masculine")
        self.__register_tag('M', "masculine")
        self.__register_tag('n', "proper noun")
        self.__register_tag('N', "proper noun")
        self.__register_tag('O', "hobbit")
        self.__register_tag('p', "plural")
        self.__register_tag('P', "plural")
        self.__register_tag('R', "brawler")
        self.__register_tag('S', "plural s")
        self.__register_tag('T', "hunter")
        self.__register_tag('U', "guardian")
        self.__register_tag('v', "initial vowel")
        self.__register_tag('V', "initial vowel")
        self.__register_tag('W', "warden")