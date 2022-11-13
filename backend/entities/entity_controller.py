from backend.common.config import Config
from backend.data_facade import DataFacade
from backend.decoders.properties_decoder import PropertiesDecoder
from backend.entities.entity_data import EntityData


class EntityTableController():
    def __init__(self, config: Config, facade: DataFacade, debug: bool = False) -> None:
        self.__config: Config = config
        self.__facade: DataFacade = facade
        self.__properties_decoder: PropertiesDecoder = PropertiesDecoder(self.__config, self.__facade)
        self.__debug: bool = debug

    def load_entities(self) -> dict[int, EntityData]:
        entity_table_ptr = self.__config.mem.read_uint(int(self.__config.entities_table_address, base=16))
        entity_manager: dict[int, EntityData] = {}

        buckets_ptr = self.__config.mem.read_uint(entity_table_ptr+(3*self.__config.pointer_size))
        if self.__debug: print(f"buckets_ptr: {hex(buckets_ptr)}")

        first_bucket_ptr = self.__config.mem.read_uint(entity_table_ptr+(4*self.__config.pointer_size))
        if self.__debug: print(f"first_bucket_ptr: {hex(first_bucket_ptr)}")

        nb_buckets = self.__config.mem.read_uint(entity_table_ptr+(5*self.__config.pointer_size))
        nb_elements = self.__config.mem.read_uint(entity_table_ptr+(5*self.__config.pointer_size)+4)
        if self.__debug: print(f"Hash Table: nb_buckets: {nb_buckets}, nb_elements: {nb_elements}")

        if buckets_ptr:
            for i in range(nb_buckets):
                first_entry = self.__config.mem.read_uint(buckets_ptr+(i*self.__config.pointer_size))
                if first_entry:
                    self.__handle_table_entry(entity_manager, first_entry)
        return entity_manager

    def __handle_table_entry(self, entity_manager: dict[int, EntityData], ptr: int) -> None:
        instance_id = self.__config.mem.read_uint(ptr)
        entity_data: EntityData = EntityData(instance_id)
        entity_manager[instance_id] = entity_data

        world_entity_ptr = self.__config.mem.read_uint(ptr+self.__config.world_entity_offset)
        self.__handle_world_entity(world_entity_ptr, entity_data)

        next_ptr = self.__config.mem.read_uint(ptr + 8)
        if next_ptr:
            self.__handle_table_entry(entity_manager, next_ptr)

    def __handle_world_entity(self, world_entity_ptr: int, entity_data: EntityData) -> None:
        world_entity_offset = 0x120 if self.__config.is_64bits else 0x98
        world_entity_construction_ptr = self.__config.mem.read_uint(world_entity_ptr+world_entity_offset)
        if world_entity_construction_ptr:
            entity_data.data_id = self.__config.mem.read_uint(world_entity_construction_ptr+world_entity_offset+self.__config.pointer_size+4)
        property_source_offset = 0xc0 if self.__config.is_64bits else 0x60
        property_source_ptr = self.__config.mem.read_uint(world_entity_ptr+property_source_offset)
        if property_source_ptr:
            prop_offset = 0x30 if self.__config.is_64bits else 0x18
            entity_data.properties = self.__properties_decoder.handle_properties(property_source_ptr, prop_offset+self.__config.pointer_size)