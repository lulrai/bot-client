import json
import os

from backend.classes.class_definition import ClassDefinition
from backend.classes.function_definition import FunctionsRegistry


class WLibData():
    def __init__(self) -> None:
        self.__classes: dict[int, ClassDefinition] = {}
        self.__labels: dict[int, str] = self.__load_hashed_strings()
        self.__functions_registry = FunctionsRegistry()

    def get_class(self, class_index: int) -> ClassDefinition:
        return self.__classes.get(class_index)

    def register_class(self, class_def: ClassDefinition) -> None:
        index = class_def.class_index
        self.__classes[index] = class_def

    @property
    def class_indices(self) -> list[int]:
        return sorted(self.__classes.keys())
    @property
    def functions_registry(self) -> FunctionsRegistry:
        return self.__functions_registry

    def get_label(self, hash: int) -> str:
        return self.__labels.get(hash)

    def __load_hashed_strings(self) -> dict[int, str]:
        with open(os.path.join('..', 'data', 'StringHashMap.json')) as inf:
            temp_hash_names = json.load(inf)
        return {int(k): v for (k, v) in temp_hash_names.items()}
