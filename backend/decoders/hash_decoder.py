from backend.common.config import GameConfig
from backend.reference.data_ref import DataReference
from typing import TypeVar
import abc


KT = TypeVar('KT')
VT = TypeVar('VT')

class HashtableDecoder(dict[KT, VT], abc.ABC):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        self.__config: GameConfig = config
        self.__key_size: int = key_size
        self.__value_offset: int = value_offset
        self.__value_size: int = value_offset

    def decode_hash_table(self, native_package_pointer: int, offset: int, package_id: int) -> dict[KT, VT]:
        buckets_ptr_offset: int = offset + 2 * self.__config.pointer_size
        buckets_ptr: int = self.__config.mem.read_uint(native_package_pointer+buckets_ptr_offset)
        first_bucket_ptr_offset: int = offset + 3 * self.__config.pointer_size
        first_bucket_ptr: int = self.__config.mem.read_uint(native_package_pointer+first_bucket_ptr_offset)
        nb_buckets_offset: int = offset + 4 * self.__config.pointer_size
        nb_buckets: int = self.__config.mem.read_uint(native_package_pointer+nb_buckets_offset)
        nb_elements: int = self.__config.mem.read_uint(native_package_pointer+nb_buckets_offset+4)
        result_map: dict[KT, VT] = {}
        if buckets_ptr is not None:
            for i in range(nb_buckets):
                first_entry: int = self.__config.mem.read_uint(buckets_ptr+(i*self.__config.pointer_size))
                if first_entry is not None:
                    self.__handle_map_entry(result_map, first_entry, package_id)
        assert len(result_map.keys()) == nb_elements
        return result_map

    def __handle_map_entry(self, result_map: dict[KT, VT], hash_table_data_ptr: int, package_id: int) -> None:
        entry_size: int = self.__value_offset + self.__value_size
        key: KT = self.parse_key(hash_table_data_ptr)
        val: VT = self.parse_value(result_map, hash_table_data_ptr, self.__value_offset, package_id)
        next: int = self.__config.mem.read_uint(hash_table_data_ptr+self.__key_size)
        result_map[key] = val
        if next: self.__handle_map_entry(result_map, next, package_id)

    @abc.abstractmethod
    def parse_key(self, hash_table_data_ptr: int) -> KT:
        pass
    @abc.abstractmethod
    def parse_value(self, result_map: dict[KT, VT], hash_table_data_ptr: int, val_offset: int, package_id: int) -> VT:
        pass

class IntLongValDecoder(HashtableDecoder):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        super().__init__(config, key_size, value_offset, value_size)
    
    def parse_key(self, hash_table_data_ptr: int) -> int:
        return self.__config.mem.read_uint(hash_table_data_ptr)

    def parse_value(self, result_map: dict[int, object], hash_table_data_ptr: int, val_offset: int, package_id: int) -> object:
        val = self.__config.mem.read_uint(hash_table_data_ptr+val_offset)
        return DataReference(val) if (package_id in (35, 117)) else val

class IntLongDecoder(HashtableDecoder):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        super().__init__(config, key_size, value_offset, value_size)
    
    def parse_key(self, hash_table_data_ptr: int) -> int:
        return self.__config.mem.read_uint(hash_table_data_ptr)

    def parse_value(self, result_map: dict[int, int], hash_table_data_ptr: int, val_offset: int, package_id: int) -> object:
        return None

class IntMultiHashDecoder(HashtableDecoder):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        super().__init__(config, key_size, value_offset, value_size)
        self.__current_key = 0

    def parse_key(self, hash_table_data_ptr: int) -> str:
        self.__current_key = self.__config.mem.read_uint(hash_table_data_ptr)
        return self.__current_key

    def parse_value(self, result_map: dict[int, list[object]], hash_table_data_ptr: int, val_offset: int, package_id: int) -> list[object]:
        key = self.__config.mem.read_uint(hash_table_data_ptr)
        assert key == self.__current_key
        val = self.__config.mem.read_uint(hash_table_data_ptr+ (self.__config.int_size + self.__config.pointer_size))
        result: list[object] = result_map.get(key)
        if result is None:
            result = []
        else:
            result_map[key] = result
        map_val = DataReference(val) if package_id == 37 else val
        result.append(map_val)
        return result

class NRHashDecoder(HashtableDecoder):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        super().__init__(config, key_size, value_offset, value_size)
    
    def parse_key(self, hash_table_data_ptr: int) -> int:
        return self.__config.mem.read_uint(hash_table_data_ptr)

    def parse_value(self, result_map: dict[int, int], hash_table_data_ptr: int, val_offset: int, package_id: int) -> int:
        return self.__config.mem.read_uint(hash_table_data_ptr+val_offset)

class NHashSetDecoder(HashtableDecoder):
    def __init__(self, config: GameConfig, key_size: int, value_offset: int, value_size: int) -> None:
        super().__init__(config, key_size, value_offset, value_size)
    
    def parse_key(self, hash_table_data_ptr: int) -> int:
        return self.__config.mem.read_uint(hash_table_data_ptr)

    def parse_value(self, result_map: dict[int, None], hash_table_data_ptr: int, val_offset: int, package_id: int) -> None:
        return None

class ContainersDecoder():
    def __init__(self, config: GameConfig) -> None:
        self.__config: GameConfig = config
        self.__intint_decoder: IntLongValDecoder = IntLongValDecoder(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, 4)
        self.__intlong_decoder: IntLongValDecoder = IntLongValDecoder(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, 8)
        longint_val_offset: int = 8+config.pointer_size if config.is_64bits else 8+config.pointer_size+4
        self.__longint_decoder: IntLongValDecoder = IntLongValDecoder(config, 8, longint_val_offset, 4)
        self.__int_decoder: IntLongDecoder = IntLongDecoder(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, 0)
        self.__long_decoder: IntLongDecoder = IntLongDecoder(config, 8, 8+config.pointer_size, 0)
        self.__intmulti_decoder: IntMultiHashDecoder = IntMultiHashDecoder(config, config.map_int_keysize, config.map_int_keysize+config.pointer_size, config.int_size+config.pointer_size+4)
        nr_keysize: int = 16 if config.is_64bits else 12
        nr_valsize: int = 12 if config.is_64bits else 4
        self.__nrhash_decoder: NRHashDecoder = NRHashDecoder(config, nr_keysize, nr_keysize+config.pointer_size, nr_valsize)
        nhash_keysize: int = 16 if config.is_64bits else 8
        self.__nhashset_decoder: NHashSetDecoder = NHashSetDecoder(config, nhash_keysize, nhash_keysize+config.pointer_size, 0)

    def handle_inint_hashtable(self, native_package_ptr: int, package_id: int) -> dict[int, object]:
        return self.__intint_decoder.decode_hash_table(native_package_ptr, 0, package_id)

    def handle_intlong_hashtable(self, native_package_ptr: int, package_id: int) -> dict[int, int]:
        return self.__intlong_decoder.decode_hash_table(native_package_ptr, 0, package_id)

    def handle_longint_hashtable(self, native_package_ptr: int, package_id: int) -> dict[int, object]:
        return self.__longint_decoder.decode_hash_table(native_package_ptr, 0, package_id)

    def handle_int_set(self, native_package_ptr: int, package_id: int) -> set[int]:
        return set(self.__int_decoder.decode_hash_table(native_package_ptr, 0, package_id).keys())

    def handle_long_set(self, native_package_ptr: int, package_id: int) -> set[int]:
        return set(self.__long_decoder.decode_hash_table(native_package_ptr, 0, package_id).keys())

    def handle_intmulti_hashtable(self, native_package_ptr: int, package_id: int) -> dict[int, list[object]]:
        return self.__intmulti_decoder.decode_hash_table(native_package_ptr, 0, package_id)

    def handle_NRHash(self, native_package_ptr: int, package_id: int) -> list[list[DataReference]]:
        decoded_map: dict[int, int] = self.__nrhash_decoder.decode_hash_table(native_package_ptr, 0, package_id)
        if decoded_map:
            result: list[list[DataReference]] = []
            keys: list[int] = sorted(decoded_map.keys())
            for key in keys:
                data_refs: list[DataReference] = [DataReference(key), DataReference(decoded_map.get(key))]
                result.append(data_refs)
            return result
        return None

    def handle_NHashSet(self, native_package_ptr: int, package_id: int) -> set[DataReference]:
        decoded_map: dict[int, None] = self.__nhashset_decoder.decode_hash_table(native_package_ptr, 0, package_id)
        if decoded_map:
            result: set[DataReference] = set()
            for key in decoded_map:
                result.add(DataReference(key))
            return result
        return None

    def handle_array(self, native_package_ptr: int, package_id: int) -> list[object]:
        array_ptr: int = self.__config.mem.read_uint(native_package_ptr)
        nb_items: int = self.__config.mem.read_uint(native_package_ptr+(self.__config.pointer_size+4))
        result: list[object] = []
        if nb_items == 0: return result
        for i in range(nb_items):
            if package_id == 104: result.append(self.__config.mem.read_long(array_ptr+(i*8)))
            else:
                val = self.__config.mem.read_uint(array_ptr+(i*4))
                result.append(DataReference(val) if package_id == 176 else val)
        return result

    def handle_list(self, native_package_ptr: int, package_id: int) -> list[object]:
        nb_items: int = self.__config.mem.read_uint(native_package_ptr+(3*self.__config.pointer_size))
        result: list[object] = []
        if nb_items == 0: return result
        list_item_ptr: int = self.__config.mem.read_uint(native_package_ptr+self.__config.pointer_size)
        while list_item_ptr is not None:
            if package_id == 111:
                result.append(self.__config.mem.read_long(list_item_ptr))
            else:
                val = self.__config.mem.read_uint(list_item_ptr)
                result.append(DataReference(val) if package_id == 182 else val)
            list_item_ptr = self.__config.mem.read_uint(list_item_ptr+self.__config.int_size)
        return result