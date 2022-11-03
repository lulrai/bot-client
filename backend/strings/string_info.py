class StringInfo():
    pass

class TableEntryStringInfo(StringInfo):
    def __init__(self, table_id: int, token_id: int) -> None:
        super().__init__()
        self.__table_id = table_id
        self.__token_id = token_id
        self.__variable_value: dict[str, object] = {}
    
    def add_variable_value(self, variable_name: str, value: object) -> None:
        self.__variable_value[str] = value

    def get_variables_count(self) -> int:
        return len(self.__variable_value.keys())

    @property
    def variables_map(self) -> dict[str, object]:
        return self.__variable_value
    @property
    def table_id(self) -> int:
        return self.__table_id
    @property
    def token_id(self) -> int:
        return self.__token_id

    def __repr__(self):
        return f'TableEntryStringInfo: table=0x{self.table_id:08X}, token=0x{self.token_id:08X}'

class LiteralStringInfo(StringInfo):
    def __init__(self, literal: str) -> None:
        super().__init__()
        self.__literal = literal

    @property
    def literal(self) -> str:
        return self.__literal