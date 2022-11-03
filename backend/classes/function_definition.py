class FunctionArgumentDefinition():
    def __init__(self, name: str, type: str) -> None:
        self.__name = name
        self.__type = type

    @property
    def name(self) -> str:
        return self.__name
    @property
    def type(self) -> str:
        return self.__type

class FunctionDefinition():
    def __init__(self, code: int, name: str) -> None:
        self.__code = code
        self.__name = name
        self.__arguments: list[FunctionArgumentDefinition] = []
        self.__byte_code_offset = 0

    @property
    def code(self) -> int:
        return self.__code
    @property
    def name(self) -> str:
        return self.__name
    @property
    def byte_code_offset(self) -> int:
        return self.__byte_code_offset
    @byte_code_offset.setter
    def byte_code_offset(self, byte_code: int) -> None:
        self.__byte_code_offset = byte_code
    
    def add_argument(self, argument: FunctionArgumentDefinition) -> None:
        self.__arguments.append(argument)

    def get_arguments(self) -> list[FunctionArgumentDefinition]:
        return self.__arguments

class FunctionsRegistry():
    def __init__(self) -> None:
        self.__map_by_name: dict[str, FunctionDefinition] = {}
        self.__map_by_code: dict[int, FunctionDefinition] = {}

    @property
    def codes(self) -> list[int]:
        return sorted(self.__map_by_code.keys())
    
    def get_function_by_code(self, code: int) -> FunctionDefinition:
        return self.__map_by_code.get(code)

    def get_function_by_name(self, name: str) -> FunctionDefinition:
        return self.__map_by_name.get(name)

    def register_function(self, function: FunctionDefinition) -> None:
        self.__map_by_code[function.code] = function
        self.__map_by_name[function.name] = function