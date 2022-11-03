from backend.reference.reference_table_controller import \
    ReferencesTableController
from backend.wdata.wstate import WStateDataSet


class ReferenceProvider():
    def get_reference(self, param_int: int) -> object:
        pass

class WStateDataSetReferenceProvider(ReferenceProvider):
    def __init__(self, dataset: WStateDataSet) -> None:
        super().__init__()
        self.__used_references: set[int] = set()
        self.__index: dict[int, object] = self.__build_map_references_to_values(dataset)
    
    def __build_map_references_to_values(self, dataset: WStateDataSet) -> dict[int, object]:
        index_map: dict[int, object] = {}
        references = dataset.references
        nb_references = len(references)
        nb_values = dataset.size()
        assert nb_references == nb_values
        for i in range(nb_values):
            reference = references[i]
            value = dataset.get_value(i)
            index_map[reference] = value
        return index_map

    def get_reference(self, param_int: int) -> object:
        if param_int in self.__index:
            self.__used_references.add(param_int)
            return self.__index.get(param_int)
        return None

    def get_unused_references(self) -> set[int]:
        return set(self.__used_references)

class ReferencesTableReferenceProvider(ReferenceProvider):
    def __init__(self, table_controller: ReferencesTableController) -> None:
        super().__init__()
        self.__table_controller: ReferencesTableController = table_controller
        self.__values_cache: dict[int, object] = {}
        self.__values_to_resolve: list[object] = []

    def get_object_stacks_to_resolve(self) -> list[object]:
        return self.__values_to_resolve

    def get_reference(self, param_int: int) -> object:
        if param_int in self.__values_cache:
            return self.__values_cache.get(param_int)
        value = self.__table_controller.get_value(param_int)
        if value:
            self.__values_to_resolve.append(value)
        self.__values_cache[param_int] = value
        return value