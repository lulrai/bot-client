import threading
from time import sleep

from backend.char_data import CharData
from backend.common.config import Config
from backend.data_facade import DataFacade


class DataExtractor():
    def __init__(self, config: Config, sync_time: int = 3) -> None:
        self.__config: Config = config
        self.__data_facade: DataFacade = DataFacade(config)
        self.__character_data: dict[str, CharData] = {}
        self.__sync_thread = threading.Thread(target=self.__sync_char, name="Char Sync", args=[sync_time])

    def sync(self) -> None:
        self.__sync_thread.daemon = True
        self.__sync_thread.start()

    def __sync_char(self, sync_time: int) -> None:
        while(True):
            try:
                curr_char_data: CharData = CharData(self.__config, self.__data_facade).parse_char()
                self.__character_data[curr_char_data.name] = curr_char_data
                print(self.__character_data)
                sleep(sync_time)
            except:
                raise

    def get_character_data(self) -> dict[str, CharData]:
        return self.__character_data

    def get_data_facade(self) -> DataFacade:
        return self.__data_facade
