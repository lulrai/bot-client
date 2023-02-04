from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.decoders.native_package_decoder import NativePackagesDecoder
from backend.decoders.wsl_decoder import WSLDecoder
from backend.reference.reference_table_entry import ReferenceTableEntry
from backend.utils.common_utils import Utils

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class ReferencesTableController():
    def __init__(self, config: GameConfig, data_facade: DataFacade) -> None:
        self.__config: GameConfig = config
        self.__entry_pointers: list[int] = []
        self.__entries_cache: dict[int, ReferenceTableEntry] = {}
        self.__wsl_decoder = WSLDecoder(config, data_facade)
        self.__natives_decoder = NativePackagesDecoder(config, data_facade)
        self.__initialize()

    def __initialize(self) -> None:
        ptr_size: int = self.__config.pointer_size
        ref_table_ptr: int = Utils.get_pointer(self.__config.mem, self.__config.references_table_address, ptr_size)
        table_ptr: int = Utils.get_pointer(self.__config.mem, ref_table_ptr, ptr_size)
        self.__num_entries: int = self.__config.mem.read_uint(ref_table_ptr + ptr_size + 4)
        self.__gc_generation: int = self.__config.mem.read_uint(ref_table_ptr + ptr_size + 12) & 0xFF
        nb_used_entries: int = self.__config.mem.read_uint(ref_table_ptr + ptr_size + 8)
        self.__entry_pointers.clear()
        for i in range(self.__num_entries):
            self.__entry_pointers.append(self.__config.mem.read_uint(table_ptr + (i*ptr_size)))
                    
    @property
    def table_size(self) -> int:
        return len(self.__entry_pointers)

    def get_entry(self, index: int) -> ReferenceTableEntry:
        entry = self.__entries_cache.get(index)
        if entry is None:
            try:
                entry = self.__load_entry(index)
                self.__entries_cache[index] = entry
            except:
                print('Failed to load entry #', index)
        return entry

    def get_value(self, index: int) -> object:
        entry: ReferenceTableEntry = self.get_entry(index)
        if entry is None: return None
        return self.__load_value(entry)

    def __load_entry(self, index: int) -> ReferenceTableEntry:
         entry_ptr: int = self.__entry_pointers[index] if index < len(self.__entry_pointers) else None
         if not entry_ptr: return None
         bit_field: int = self.__config.mem.read_uint(entry_ptr)
         gc_generation: int = bit_field & 0xFF
         if gc_generation != self.__gc_generation: return None
         package_factory_info_ptr: int = self.__config.mem.read_uint(entry_ptr+self.__config.int_size)
         wsl_package_ptr: int = self.__config.mem.read_uint(entry_ptr+(self.__config.int_size + self.__config.pointer_size))
         native_package_ptr: int = self.__config.mem.read_uint(entry_ptr+(self.__config.int_size + 2 * self.__config.pointer_size))
         package_id: int = self.__config.mem.read_uint(package_factory_info_ptr)
         return ReferenceTableEntry(index, package_id, bit_field, package_factory_info_ptr, wsl_package_ptr, native_package_ptr)

    def __load_value(self, entry: ReferenceTableEntry) -> object:
        result: object = None
        try:
            bit_field: int = entry.bitfield
            package_factory_info_ptr: int = entry.package_factory_info_ptr
            is_native: bool = (bit_field & 0x10000000) != 0
            if not is_native:
                wsl_package_ptr: int = entry.wsl_package_ptr
                if wsl_package_ptr: return self.__wsl_decoder.handle_class_instance(package_factory_info_ptr, wsl_package_ptr)
            else:
                native_package_ptr: int = entry.native_package_ptr
                return self.__natives_decoder.handle_native(package_factory_info_ptr, native_package_ptr)
        except:
            print('Caught exception for entry #', entry.index)
        return None
