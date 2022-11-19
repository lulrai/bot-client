import threading
from time import sleep

from pymem.exception import MemoryReadError

from backend.char_data import CharData
from backend.common.config import Config
from backend.data_facade import DataFacade


class DataExtractor():
    def __init__(self, config: Config, sync_time: int = 3) -> None:
        self.__config: Config = config
        self.__data_facade: DataFacade = DataFacade(config)
        self.__character_data: dict[str, CharData] = {}
        self.__thread_event = threading.Event()
        self.__sync_time = sync_time
        self.__sync_thread = threading.Thread(target=self.__sync_char, name="Char Sync", args=[self.__sync_time, self.__thread_event])
        self.__sync_thread.daemon = True

    def sync(self) -> None:
        self.__sync_thread = threading.Thread(target=self.__sync_char, name="Char Sync", args=[self.__sync_time, self.__thread_event])
        self.__sync_thread.daemon = True
        self.__thread_event.clear()
        self.__sync_thread.start()

    def stop_sync(self) -> None:
        self.__thread_event.set()
        self.__sync_thread.join()

    def sync_enabled(self) -> bool:
        return self.__sync_thread.is_alive()

    def __sync_char(self, sync_time: int, event: threading.Event) -> None:
        while(True):
            if event.is_set():
                break
            try:
                curr_char_data: CharData = CharData(self.__config, self.__data_facade).parse_char()
                if not curr_char_data.name: continue
                self.__character_data[curr_char_data.name] = curr_char_data
                print(self.__character_data)
                sleep(sync_time)
            except MemoryReadError as mem_read_err:
                if mem_read_err.args[0].startswith('Could not read memory at: 0') and not self.__character_data:
                    sleep(sync_time)
                continue

    def get_character_data(self) -> dict[str, CharData]:
        return self.__character_data

    def get_data_facade(self) -> DataFacade:
        return self.__data_facade
