from __future__ import annotations


class AttributeDefinition():
    REFERENCE = 1
    INTEGER = 2
    FLOAT = 3
    LONG = 130
    UNUSED = 131
    TIMESTAMP = 195
    VAR_TYPE_NAMES = {
        REFERENCE: 'reference',
        INTEGER: 'int',
        FLOAT: 'float',
        LONG: 'long',
        UNUSED: 'type131',
        TIMESTAMP: 'timestamp'
    }

    def __init__(self, parent_class: ClassDefinition, name: str, index: int, attr_type: int) -> None:
        self.__parent_class = parent_class
        self.__name = name
        self.__index = index
        self.__type = attr_type

    @property
    def parent_class(self) -> ClassDefinition:
        return self.__parent_class
    @property
    def name(self) -> str:
        return self.__name
    @property
    def index(self) -> int:
        return self.__index
    @property
    def type(self) -> int:
        return self.__type

class ClassDefinition():    
    def __init__(self, class_index: int, name: str) -> None:
        self.__class_index = class_index
        self.__name = name
        self.__attributes: list[AttributeDefinition] = []
        self.__parent: ClassDefinition = None
        self.__raw_size = 0

    @property
    def class_index(self) -> int:
        return self.__class_index
    @property
    def name(self) -> str:
        return self.__name if self.__name else str(self.__class_index)
    @property
    def parent(self) -> ClassDefinition:
        return self.__parent
    @parent.setter
    def parent(self, parent: ClassDefinition) -> None:
        self.__parent = parent
    @property
    def raw_size(self) -> int:
        return self.__raw_size
    @raw_size.setter
    def raw_size(self, raw_sz: int) -> None:
        self.__raw_size = raw_sz
    @property
    def attributes_count(self) -> int:
        return len(self.__attributes)
    @property
    def attributes(self) -> list[AttributeDefinition]:
        return self.__attributes
    @property
    def sorted_attributes(self) -> list[AttributeDefinition]:
        return sorted(self.__attributes, key=lambda x: x.index)
    
    def get_attribute_by_name(self, attr_name: str) -> AttributeDefinition:
        return next((x for x in self.__attributes if x.name == attr_name), None)
    
    def add_attribute(self, attribute: AttributeDefinition) -> None:
        self.__attributes.append(attribute)

class ClassInstance():
    def __init__(self, class_def: ClassDefinition) -> None:
        self.__class_def = class_def
        self.__values: list[object] = [None] * self.__class_def.attributes_count

    @property
    def class_def(self) -> ClassDefinition:
        return self.__class_def
    
    def set_attr_val(self, attribute: AttributeDefinition, value: object) -> None:
        index = self.__class_def.sorted_attributes.index(attribute)
        self.__values[index] = value

    def get_attr_val(self, attribute: AttributeDefinition = None, attr_name: str = None, index: int = None) -> object:
        if index >= 0:
            return self.__values[index]
        if attribute:
            index = self.__class_def.sorted_attributes.index(attribute)
            return self.__values[index]
        if attr_name:
            index = self.__class_def.sorted_attributes.index(self.__class_def.get_attribute_by_name(attr_name))
            return self.__values[index]
        return None