import os

from backend.common.config import GameConfig
from backend.common.dat_archive import DATArchive

DAT_FILES = ("general", "anim", "gamelogic", "local_English", 
        "highres", "highres_aux_1", "highres_aux_2", "mesh",
        "surface", "surface_aux_1", "sound", "sound_aux_1",
        "cell_1", "cell_2", "cell_3", "cell_4", "cell_14",
        "map_1", "map_2", "map_3", "map_4", "map_14")

class DatFilesManager():
    def __init__(self, config: GameConfig, debug: bool = False) -> None:
        self.__archives: dict[str, DATArchive] = {}
        self.__debug: bool = debug
        for dat in DAT_FILES:
            aux = "x" if dat.find('aux') != -1 else ""
            if self.__debug: print('Opening and working with dat_file', f"client_{dat}.dat{aux}")
            archive = DATArchive(os.path.join(config.lotro_client_dir, f"client_{dat}.dat{aux}"))
            archive.open()
            self.__archives[dat] = archive
        
    def get_archive(self, key: str) -> DATArchive:
        if self.__debug: print('File info:', self.__archives[key].file_input.name)
        return self.__archives[key]

    def close(self) -> None:
        for archive in self.__archives.values():
            archive.close()
        self.__archives.clear()