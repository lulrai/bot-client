from __future__ import annotations

from backend.properties.properties_type import PropertyType


class PropertyDef():
    def __init__(self, pid: int, name: str, type: PropertyType) -> None:
        self.__propertyId = pid
        self.__name = name
        self.__property_type = type
        self.__data = 0
        self.__min_val = None
        self.__max_val = None
        self.__default_val = None
        self.__child_prop: list[PropertyDef] = []  

    @property
    def pid(self) -> int:
        return self.__propertyId

    @property
    def name(self) -> str:
        return self.__name

    @property
    def ptype(self) -> PropertyType:
        return self.__property_type
    @ptype.setter
    def ptype(self, ptype: PropertyType) -> None:
        self.__property_type = ptype

    @property
    def data(self) -> int:
        return self.__data
    @data.setter
    def data(self, data: int) -> None:
        self.__data = data

    @property
    def min_val(self) -> object:
        return self.__min_val
    @min_val.setter
    def min_val(self, min_val: object) -> None:
        self.__min_val = min_val

    @property
    def max_val(self) -> object:
        return self.__max_val
    @max_val.setter
    def max_val(self, max_val: object) -> None:
        self.__max_val = max_val

    @property
    def def_val(self) -> object:
        return self.__default_val
    @def_val.setter
    def def_val(self, def_val: object) -> None:
        self.__default_val = def_val

    @property
    def child_props(self):
        return self.__child_prop

    def set_child_prop(self, prop_def: PropertyDef) -> None:
        if prop_def is None: raise Exception("Cannot have None child property.")
        self.__child_prop.append(prop_def)
    def has_child_prop(self, propId: int) -> bool:
        if self.__child_prop:
            for c_prop in self.__child_prop:
                if c_prop.pid == propId: return True
        return False