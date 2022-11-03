from backend.properties.properties_def import PropertyDef

class PropertyValue():
    def __init__(self, prop_def: PropertyDef, val: object, complement: object) -> None: 
        self.__definition = prop_def
        self.__value = val
        self.__complement = complement
    
    @property
    def prop_definition(self) -> PropertyDef:
        return self.__definition

    @property
    def value(self) -> object:
        return self.__value

    @property
    def complement(self) -> object:
        return self.__complement

class ArrayPropertyValue(PropertyValue):
    def __init__(self, prop_def: PropertyDef, values: list[PropertyValue]) -> None:
        super().__init__(prop_def, self.__build_values_array(values), self.__build_complements_array(values))
        self.__values = values

    def get_values(self) -> list[PropertyValue]:
        return self.__values

    def __build_values_array(self, values: list[PropertyValue]) -> list[object]:
        ret = [0] * len(values)
        for i in range(len(values)):
            ret[i] = values[i].value
        return ret

    def __build_complements_array(self, values: list[PropertyValue]) -> list[object]:
        ret = [0] * len(values)
        for i in range(len(values)):
            ret[i] = values[i].complement
        return ret