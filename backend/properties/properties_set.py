from __future__ import annotations

from backend.properties.properties_val import PropertyValue


class Properties():
    def __init__(self) -> None:
        self.__props: dict[str, PropertyValue] = {}

    @property
    def props(self) -> dict[str, PropertyValue]:
        return self.__props

    def has_property(self, name: str) -> bool:
        return name in self.__props

    def get_property(self, name: str) -> object:
        return self.__props.get(name).value if self.__props.get(name) else None

    def get_propery_value_by_name(self, name: str) -> PropertyValue:
        return self.__props.get(name)

    def set_property(self, property_val: PropertyValue) -> None:
        self.__props[property_val.prop_definition.name] = property_val