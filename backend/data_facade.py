import json
import os

from backend.classes.function_definition import (FunctionArgumentDefinition,
                                                 FunctionDefinition,
                                                 FunctionsRegistry)
from backend.common.config import Config
from backend.managers.datfiles_manager import DatFilesManager
from backend.managers.enums_manager import EnumManager
from backend.managers.properties_manager import (PropertiesRegistry,
                                                 PropertyDefinitionsLoader)
from backend.managers.strings_manager import StringsManager
from backend.properties.dbprops_loader import DBPropertiesLoader
from backend.properties.properties_set import Properties
from backend.reference.reference_provider import WStateDataSetReferenceProvider
from backend.reference.reference_resolver import ReferencesResolver
from backend.wdata.wlib_data import WLibData
from backend.wdata.wlib_loader import WLibLoader
from backend.wdata.wstate import WStateDataSet
from backend.wdata.wstate_loader import WStateLoader


class DataFacade():
    def __init__(self, config: Config, debug: bool = False) -> None:
        self.__dat_manager = DatFilesManager(config)
        self.__property_registry: PropertiesRegistry = None
        self.__strings_manager: StringsManager = StringsManager(self)
        self.__enum_manager: EnumManager = EnumManager(self)
        self.__wlib: WLibData = None
        self.__debug: bool = debug

    def load_data(self, data_id: int) -> bytearray:
        keys = self.__get_archives(data_id)
        for key in keys:
            if self.__debug: 
                print("Loading entry from:", key)
            archive = self.__dat_manager.get_archive(key)
            if archive: 
                return archive.load_entry_by_id(data_id)
        return None

    def __load_properties_registry(self) -> PropertiesRegistry:
        data = self.load_data(872415232)
        if data: 
            return PropertyDefinitionsLoader.decode_master_property(data)
        return None

    def load_properties(self, data_id: int) -> Properties:
        return_props: Properties = None
        property_raw_data: bytearray = self.load_data(data_id)
        if property_raw_data is not None:
            loader: DBPropertiesLoader = DBPropertiesLoader(self)
            return_props = loader.decode_properties_resource(property_raw_data)
        return return_props

    def get_wlib_data(self) -> WLibData:
        if self.__wlib:
            return self.__wlib
        data = self.load_data(1442840576)
        wlib_data = WLibData()
        wlib_loader = WLibLoader(wlib_data)
        wlib_loader.decode(data)
        self.__load_functions(wlib_data.functions_registry)
        return wlib_data

    def load_wstate(self, data_id: int) -> WStateDataSet:
        wstate_dataset: WStateDataSet = None
        data = self.load_data(data_id)
        if data:
            wlib_data = WLibData()
            wstate_loader = WStateLoader(self, wlib_data)
            wstate_dataset = wstate_loader.decode_wstate(data)
            self.__resolve_dataset(wstate_dataset)
        return wstate_dataset

    def __resolve_dataset(self, dataset: WStateDataSet) -> None:
        reference_provider: WStateDataSetReferenceProvider = WStateDataSetReferenceProvider(dataset)
        resolver: ReferencesResolver = ReferencesResolver(reference_provider)
        nb_values = dataset.size()
        for i in range(nb_values):
            value = dataset.get_value(i)
            if value:
                resolver.resolve_references_in_val(value)
        orphan_references: list[int] = list(dataset.references)
        orphan_references = [x for x in orphan_references if x not in reference_provider.get_unused_references()]
        dataset.set_orphan_references(orphan_references)

    def get_properties_registry(self) -> PropertiesRegistry:
        if self.__property_registry is None:
            self.__property_registry = self.__load_properties_registry()
        return self.__property_registry

    def get_strings_manager(self) -> StringsManager:
        return self.__strings_manager

    def get_enums_manager(self) -> EnumManager:
        return self.__enum_manager

    def __load_functions(self, functions_registry: FunctionsRegistry) -> None:
        with open(os.path.join('..', 'data', 'Functions.json'), 'r') as json_file:
            functions_list: list[dict] = json.load(json_file)
            for function in functions_list:
                code = int(function.get('code'))
                function_name = function.get('name')
                byte_code_offset = int(function.get('byteCodeOffset'))
                func: FunctionDefinition = FunctionDefinition(code, function_name)
                func.byte_code_offset = byte_code_offset
                func_args = function.get('argument')
                if func_args:
                    for argument in func_args:
                        arg_name = argument.get('name')
                        arg_type = argument.get('type')
                        func_arg: FunctionArgumentDefinition = FunctionArgumentDefinition(arg_name, arg_type)
                        func.add_argument(func_arg)
                functions_registry.register_function(func)

    def __get_archives(self, data_id: int):
        if data_id >= 16777216 and data_id <= 33554431: return ["general"]
        if (data_id >= 67108864 and data_id <= 83886079): return ["general"]
        if (data_id >= 100663296 and data_id <= 117440511): return ["mesh"]
        if (data_id >= 117440512 and data_id <= 134217727): return ["gamelogic"]
        if (data_id >= 167772160 and data_id <= 184549375): return ["sound", "sound_aux_1"]
        if (data_id >= 234881028 and data_id <= 240123903): return ["general"]
        if (data_id >= 251658240 and data_id <= 268435455): return ["general"]
        if (data_id >= 402653184 and data_id <= 419430399): return ["general"]
        if (data_id >= 520093696 and data_id <= 536870911): return ["general"]
        if (data_id >= 536870912 and data_id <= 553648127): return ["general"]
        if (data_id >= 570425344 and data_id <= 587202559): return ["general", "local_English"]
        if (data_id >= 587202560 and data_id <= 603979775): return ["general"]
        if (data_id >= 620756992 and data_id <= 654311423): return ["local_English"]
        if (data_id >= 671088640 and data_id <= 687865855): return ["general"]
        if (data_id >= 721420288 and data_id <= 738197503): return ["general"]
        if (data_id >= 805306368 and data_id <= 822083583): return ["general"]
        if (data_id >= 822083584 and data_id <= 838860799): return ["general"]
        if (data_id >= 872415232 and data_id <= 872415232): return ["gamelogic"]
        if (data_id >= 1073741824 and data_id <= 1090519039): return ["general"]
        if (data_id >= 1090519040 and data_id <= 1107296255): return ["highres", "highres_aux_1", "highres_aux_2", "surface", "surface_aux_1", "local_English"]
        if (data_id >= 1191182336 and data_id <= 1207959551): return ["gamelogic"]
        if (data_id >= 1442840576 and data_id <= 1459617791): return ["gamelogic"]
        if (data_id >= 1879048192 and data_id <= 2013265919): return ["gamelogic"]
        if (data_id >= 2013265920 and data_id <= 2147483647): return ["gamelogic", "local_English"]
        if (data_id >= 2147549184 and data_id <= 2147614719): return ["cell_1"]
        if (data_id >= 2147614720 and data_id <= 2147680255): return ["cell_2"]
        if (data_id >= 2147680256 and data_id <= 2147745791): return ["cell_3"]
        if (data_id >= 2147745792 and data_id <= 2147811327): return ["cell_4"]
        if (data_id >= 2148401152 and data_id <= 2148466687): return ["cell_14"]
        if (data_id >= 2149646336 and data_id <= 2149711871): return ["cell_1"]
        if (data_id >= 2149711872 and data_id <= 2149777407): return ["cell_2"]
        if (data_id >= 2149777408 and data_id <= 2149842943): return ["cell_3"]
        if (data_id >= 2149842944 and data_id <= 2149908479): return ["cell_4"]
        if (data_id >= 2150498304 and data_id <= 2150563839): return ["cell_14"]
        if (data_id >= 2151743488 and data_id <= 2151809023): return ["cell_1"]
        if (data_id >= 2151809024 and data_id <= 2151874559): return ["cell_2"]
        if (data_id >= 2151874560 and data_id <= 2151940095): return ["cell_3"]
        if (data_id >= 2151940096 and data_id <= 2152005631): return ["cell_4"]
        if (data_id >= 2152595456 and data_id <= 2152660991): return ["cell_14"]
        return None
