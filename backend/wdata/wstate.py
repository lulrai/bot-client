class WStateDataSet():
    def __init__(self) -> None:
        self.__references: list[int] = []
        self.__values: list[object] = []
        self.__orphan_references: list[int] = []

    def add_reference(self, reference: int) -> None:
        self.__references.append(reference)

    def get_value_for_reference(self, reference: int) -> object:
        index = -1
        try:
            index = self.__references.index(reference)
            return self.__values[index]
        except:
            return None

    @property
    def references(self) -> list[int]:
        return self.__references
    @property
    def orphan_references(self) -> list[int]:
        return self.__orphan_references

    def add_value(self, value: object) -> None:
        self.__values.append(value)

    def get_value(self, index: int) -> object:
        return self.__values[index]

    def size(self) -> int:
        return len(self.__values)

    def set_orphan_references(self, references: list[int]) -> None:
        self.__orphan_references.clear()
        self.__orphan_references.extend(references)
        self.__orphan_references.sort()