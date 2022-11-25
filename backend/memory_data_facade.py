from backend.common.client import ClientData
from backend.common.config import Config
from backend.data_facade import DataFacade
from backend.entities.entity_controller import EntityTableController
from backend.entities.entity_data import EntityData
from backend.properties.properties_set import Properties
from backend.reference.reference_table_controller import \
    ReferencesTableController
from backend.wdata.wsl_inspector import WSLInspector


class MemoryDataFacade():
    def __init__(self, config: Config, facade: DataFacade, debug: bool = False) -> None:
        self.__entities_manager: dict[int, EntityData] = EntityTableController(config, facade).load_entities()
        self.__references_table_controller: ReferencesTableController = ReferencesTableController(config, facade)
        self.__client_data: ClientData = ClientData(config, facade, debug).load_client_data()
        #self.__storage_data_controller: StorageDataController = StorageDataController(config, facade)

    def get_entities_manager(self) -> dict[int, EntityData]:
        return self.__entities_manager
    
    def get_reference_table_controller(self) -> ReferencesTableController:
        return self.__references_table_controller

    def get_client_data(self) -> ClientData:
        return self.__client_data

    def get_account_data(self) -> Properties:
        return self.__client_data.account_data if self.__client_data else None

class MemoryExtractionSession():
    def __init__(self, config: Config, data_facade: DataFacade, debug: bool = False) -> None:
        self.__data_facade: DataFacade = data_facade
        self.__memory_data_facade: MemoryDataFacade = MemoryDataFacade(config, data_facade, debug)
        if self.__memory_data_facade: self.__wsl_inspector: WSLInspector = WSLInspector(self.__memory_data_facade.get_reference_table_controller())

    def get_data_facade(self) -> DataFacade:
        return self.__data_facade

    def get_memory_facade(self) -> MemoryDataFacade:
        return self.__memory_data_facade

    def get_wsl_inspector(self) -> WSLInspector:
        return self.__wsl_inspector