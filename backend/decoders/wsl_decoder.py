from __future__ import annotations

from typing import TYPE_CHECKING

from backend.classes.class_definition import AttributeDefinition, ClassInstance
from backend.common.config import Config

if TYPE_CHECKING:
    from backend.data_facade import DataFacade

class WSLDecoder():
    def __init__(self, config: Config, data_facade: DataFacade) -> None:
        self.__config = config
        self.__data_facade = data_facade

    def handle_class_instance(self, package_factor_ptr: int, wsl_package_ptr: int) -> ClassInstance:
        package_id = self.__config.mem.read_uint(package_factor_ptr)
        if package_id == 0: return None
        class_def = self.__data_facade.get_wlib_data().get_class(package_id)
        if class_def is None: return None
        class_instance: ClassInstance = ClassInstance(class_def)
        attributes: list[AttributeDefinition] = class_def.sorted_attributes
        offset = 0
        for attribute in attributes:
            value: object = self.__read_value(attribute, wsl_package_ptr, offset)
            class_instance.set_attr_val(attribute, value)
        return class_instance

    def __read_value(self, attribute: AttributeDefinition, wsl_package_ptr: int, offset: int) -> object:
        type: int = attribute.type
        result: object = None
        if type in (1, 2): # REFERENCE, INTEGER
            result = self.__config.mem.read_uint(wsl_package_ptr+offset)
            offset += 4
        elif type == 3: # FLOAT
            result = self.__config.mem.read_float(wsl_package_ptr+offset)
            offset += 4
        elif type in (130, 131, 195): # LONG, SIGNED_DOUBLE, DOUBLE
            v1 = self.__config.mem.read_uint(wsl_package_ptr+offset) & 0xFFFFFFFF
            offset += 4
            type_code = self.__config.mem.read_uint(wsl_package_ptr+offset)
            assert type_code == attribute.type
            offset += 4
            v2 = self.__config.mem.read_uint(wsl_package_ptr+offset) & 0xFFFFFFFF
            offset += 4
            result = (v2 << 32) + v1
        else:
            print('Unsupported type:', type)
        got_type_code = self.__config.mem.read_uint(wsl_package_ptr+offset)
        print('Got type code:', got_type_code)
        offset += 4
        return result