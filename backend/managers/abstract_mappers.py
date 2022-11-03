class DidMapEntry():
    def __init__(self, key: int, did: int, label: str) -> None:
        self.__key: int = key
        self.__did: int = did
        self.__label: str = label

    @property
    def key(self) -> int:
        return self.__key
    @property
    def did(self) -> int:
        return self.__did
    @property
    def label(self) -> str:
        return self.__label
        
class AbstractMapper():
    def __init__(self, data_id: int) -> None:
        self.__data_id: int = data_id

    @property
    def data_id(self) -> int:
        return self.__data_id

    def get_label(self, code: str) -> str:
        pass

class DIDMapper(AbstractMapper):
    def __init__(self, data_id: int) -> None:
        super().__init__(data_id)
        self.__map: dict[int, DidMapEntry] = {}

    def add(self, key: int, data_id: int, label: str) -> None:
        entry: DidMapEntry = DidMapEntry(key, data_id, label)
        self.__map[key] = entry

    def get_entry(self, key: int) -> DidMapEntry:
        return self.__map.get(key)

    def get_data_id_for_label(self, label: str) -> int:
        for entry in self.__map.values():
            if label in entry.label: return entry.did
        return None

    def get_keys(self) -> list[int]:
        return sorted(list(self.__map.keys()))

    def get_labels(self) -> list[str]:
        return sorted([x.label for x in self.__map.values()])

    def get_label(self, code: int) -> str:
        entry: DidMapEntry = self.__map.get(code)
        return entry.label if entry else None

class EnumMapper(AbstractMapper):
    def __init__(self, data_id: int) -> None:
        super().__init__(data_id)
        self.__base_data_id = 0
        self.__tokens: dict[int, str] = {}

    @property
    def base_data_id(self) -> int:
        return self.__base_data_id
    @base_data_id.setter
    def base_data_id(self, base_data_id: int) -> None:
        self.__base_data_id = base_data_id

    def get_tokens(self) -> list[int]:
        token_list = list(self.__tokens.keys())
        token_list.sort()
        return token_list

    def add_enum(self, token: int, value: str) -> None:
        self.__tokens[token] = value

    def get_str(self, token: int) -> str:
        return self.__tokens.get(token)

    def get_label(self, code: int) -> str:
        return self.get_str(code)