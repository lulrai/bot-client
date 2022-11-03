from backend.classes.class_definition import ClassDefinition

class DataReference():
    def __init__(self, reference: int) -> None:
        self.__reference = reference

    @property
    def reference(self) -> int:
        return self.__reference

class DataIdentification():
    def __init__(self, did: int, name: str, wClass: ClassDefinition) -> None:
        self.__did = did
        self.__name = name
        self.__wClass = wClass

    @property
    def did(self) -> int:
        return self.__did
    @property
    def name(self) -> str:
        return self.__name
    @property
    def wClass(self) -> ClassDefinition:
        return self.__wClass
    @property
    def wClass_name(self) -> str:
        return self.__wClass.name if self.__wClass else '?'