from __future__ import annotations

from typing import TypeVar

from backend.classes.class_definition import AttributeDefinition, ClassInstance
from backend.reference.data_ref import DataReference
from backend.reference.reference_provider import ReferenceProvider


class ReferencesResolver():
    _KT = TypeVar("_KT") #  key type
    _VT = TypeVar("_VT") #  value type

    def __init__(self, reference_provider: ReferenceProvider) -> None:
        self.__reference_provider = reference_provider

    def resolve_references_in_val(self, value: object) -> None:
        if value is None: return
        if isinstance(value, ClassInstance):
            class_instance: ClassInstance = value
            self.__resolve_references_in_class_instance(class_instance)
        elif isinstance(value, dict):
            map_refs: dict[ReferencesResolver._KT, object] = value
            self.__resolve_references_in_map_values(map_refs)
        elif isinstance(value, list):
            list_refs: list[object] = value
            self.__resolve_references_in_list_values(list_refs)

    def __resolve_references_in_class_instance(self, class_instance: ClassInstance) -> None:
        class_def = class_instance.class_def
        for attribute in class_def.attributes:
            if attribute.type == AttributeDefinition.REFERENCE:
                attribute_val = class_instance.get_attr_val(attribute)
                if isinstance(attribute_val, int):
                    reference: int = attribute_val
                    solved_val = self.__resolve(reference)
                    class_instance.set_attr_val(attribute, solved_val)

    def __resolve_references_in_map_values(self, map_refs: dict[ReferencesResolver._KT, object]) -> None:
        for key, value in map_refs.items():
            if isinstance(value, DataReference):
                data_reference: DataReference = value
                reference = data_reference.reference
                value = self.__resolve(reference)
            else:
                self.resolve_references_in_val(value)
        
    def __resolve_references_in_list_values(self, list_refs: list[object]) -> None:
        for i in range(len(list_refs)):
            value = list_refs[i]
            if isinstance(value, DataReference):
                data_reference: DataReference = value
                reference = data_reference.reference
                list_refs[i] = self.__resolve(reference)
            else:
                self.resolve_references_in_val(value)

    def __resolve(self, reference: int) -> object:
        if reference >= 1879048192:
            return reference
        elif reference > 0:
            return self.__reference_provider.get_reference(reference)
        else:
            return None
