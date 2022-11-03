from __future__ import annotations

class FileEntry():
    def __init__(self, index: int, fileId: int, fileOffset: int, version: int, timestamp: int, size: int, blockSize: int, flags: int, policy: int) -> None:
        self.__index = index
        self.__file_id = fileId
        self.__file_offset = fileOffset
        self.__version = version
        self.__timestamp = timestamp
        self.__size = size
        self.__block_size = blockSize
        self.__flags = flags
        self.__policy = policy
        self.__is_compressed = (self.flags & 0x1 != 0)
    
    @property
    def index(self) -> int:
        return self.__index
    @property
    def file_id(self) -> int:
        return self.__file_id
    @property
    def file_offset(self) -> int:
        return self.__file_offset
    @property
    def version(self) -> int:
        return self.__version
    @property
    def timestamp(self) -> int:
        return self.__timestamp
    @property
    def size(self) -> int:
        return self.__size
    @property
    def block_size(self) -> int:
        return self.__block_size
    @property
    def flags(self) -> int:
        return self.__flags
    @property
    def policy(self) -> int:
        return self.__policy
    @property
    def is_compressed(self) -> bool:
        return self.__is_compressed

class DirectoryEntry():
    def __init__(self, parent: DirectoryEntry, offset: int) -> None:
        self.__parent = parent
        self.__offset = offset
        self.__file_entries: list[FileEntry] = []
        self.__dir_entries: list[DirectoryEntry] = []

    @property
    def offset(self) -> int:
        return self.__offset
    @property
    def files(self) -> list:
        return self.__file_entries
    @property
    def dirs(self) -> list:
        return self.__dir_entries

    def add_dir(self, dir_entry: DirectoryEntry) -> None:
        self.__dir_entries.append(dir_entry)

    def add_file(self, file_entry: FileEntry) -> None:
        self.__file_entries.append(file_entry)
