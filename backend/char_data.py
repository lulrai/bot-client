from __future__ import annotations

from typing import TYPE_CHECKING

from backend.entities.entity_data import EntityData
from backend.memory_data_facade import (MemoryDataFacade,
                                        MemoryExtractionSession)

if TYPE_CHECKING:
    from backend.common.config import Config
    from backend.data_facade import DataFacade
    from backend.properties.properties_set import Properties

class CharData():
    def __init__(self, config: Config, data_facade: DataFacade) -> None:
        self.__config: Config = config
        self.__data_facade: DataFacade = data_facade
        self.__memory_extraction_session: MemoryExtractionSession = None
        self.__entity_data: EntityData = None
        self.__name = ''

    def parse_char(self) -> CharData:
        self.__memory_extraction_session: MemoryExtractionSession = MemoryExtractionSession(self.__config, self.__data_facade, True)
        memory_facade: MemoryDataFacade = self.__memory_extraction_session.get_memory_facade()
        entities_mngr: dict[int, EntityData] = memory_facade.get_entities_manager()
            
        entity_ids: list[int] = sorted(entities_mngr.keys())
        for entity_id in entity_ids:
            entity_data: EntityData = entities_mngr.get(entity_id)
            props: Properties = entity_data.properties
            if props:
                char_type = props.get_property('CharacterType')
                if char_type and char_type == 2:
                    self.__name = entity_data.properties.get_property('Name')
                    self.__entity_data = entity_data
        return self

    @property
    def entity_data(self) -> EntityData:
        return self.__entity_data
    @property
    def name(self) -> str:
        return self.__name
    
    def get_memory_extraction_session(self) -> MemoryExtractionSession:
        return self.__memory_extraction_session