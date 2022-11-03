from backend.properties.properties_set import Properties


class EntityData():
    def __init__(self, entity_id: int) -> None:
        self.__entity_id: int = entity_id
        self.__properties: Properties = None
        self.__data_id: int = 0
    
    @property
    def entity_id(self) -> int:
        return self.__entity_id
    
    @property
    def data_id(self) -> int:
        return self.__data_id
    @data_id.setter
    def data_id(self, data_id: int) -> None:
        self.__data_id = data_id
    
    @property
    def properties(self) -> Properties:
        return self.__properties
    @properties.setter
    def properties(self, properties: Properties) -> None:
        self.__properties = properties