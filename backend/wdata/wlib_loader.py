import io
import json
import os

from backend.classes.class_definition import (AttributeDefinition,
                                              ClassDefinition)
from backend.utils.common_utils import Utils
from backend.wdata.wlib_data import WLibData


class WLibLoader():
    BYTECODE = 1
    MESSAGES = 2
    CLASS_DEFS = 16
    UNKNOWN = 64
    CLASS_VARS = 512
    PARENTS_MAP = 1024
    def __init__(self, data: WLibData) -> None:
        self.__data: WLibData = data
        self.__classes_list: list[ClassDefinition] = []
        self.__class_names = self.__load_class_names()

    def __load_class_names(self) -> dict[int, str]:
        read_class_names: dict[int, str] = {}
        with open(os.path.join('..', 'data', 'PackageNames.json'), 'r') as json_file:
            class_names_list = json.load(json_file)
            for class_info in class_names_list:
                read_class_names[int(class_info['index'])] = class_info['name']
        return read_class_names

    def decode(self, buffer: bytearray) -> None:
        ins: io.BytesIO = io.BytesIO(buffer)
        did = Utils.read_uint32(ins)
        stop_code = Utils.read_uint32(ins)
        unknown2 = Utils.read_uint32(ins)
        unknown3 = Utils.read_uint32(ins)
        while Utils.bytes_available(ins) > 4:
            four_cc = Utils.read_uint32(ins)
            if four_cc == -19131852:
                chunk_type = Utils.read_uint32(ins)
                size = Utils.read_uint32(ins)
                data = bytearray(ins.read(size))
                self.__load_chunk(chunk_type, data)
                continue
            if four_cc == stop_code:
                assert Utils.read_int8(ins) == 1
                continue
    
    def __load_chunk(self, chunk_type: int, data: bytearray) -> None:
        ins: io.BytesIO = io.BytesIO(data)
        if chunk_type == self.BYTECODE:
            size = Utils.read_uint32(ins)
            bytearray(ins.read(size))
        elif chunk_type == self.MESSAGES:
            count = Utils.read_uint32(ins)
            for i in range(count):
                Utils.read_prefixed_utf16(ins)
            count = Utils.read_uint32(ins)
            if count > 0:
                for i in range(count):
                    Utils.read_prefixed_array(ins, 'L', 'L')
        elif chunk_type == self.CLASS_DEFS:
            count = Utils.read_vle(ins)
            for i in range(count):
                is_defined = Utils.read_bool(ins)
                if is_defined:
                    class_def: ClassDefinition = self.__load_class_def(ins)
                    self.__classes_list.append(class_def)
                else:
                    self.__classes_list.append(None)
        elif chunk_type == self.CLASS_VARS:
            num_classes = Utils.read_tsize(ins)
            for i in range(num_classes):
                class_index = Utils.read_uint32(ins)
                class_def: ClassDefinition = self.__data.get_class(class_index)
                assert class_def is not None
                num_vars = Utils.read_tsize(ins)
                for j in range(num_vars):
                    name_hash = Utils.read_uint32(ins)
                    name = self.__data.get_label(name_hash)
                    if name is None: name = str(name_hash)
                    index = Utils.read_uint16(ins)
                    value_type_code = Utils.read_uint8(ins)
                    class_variable: AttributeDefinition = AttributeDefinition(class_def, name, index, value_type_code)
                    class_def.add_attribute(class_variable)
        elif chunk_type == self.PARENTS_MAP:
            values = Utils.read_prefixed_array(ins, 'L', 'L')
            expected_len = len(self.__classes_list)
            length = len(values)
            assert length == expected_len
            for i in range(length):
                parent_class_index = values[i]
                if parent_class_index > 0:
                    class_def = self.__classes_list[i]
                    if class_def:
                        parent_class_def = self.__data.get_class(parent_class_index)
                        class_def.parent = parent_class_def
        else:
            print('WARNING: Unmanaged chunk type:', chunk_type)

    def __load_class_def(self, ins: io.BytesIO) -> ClassDefinition:
        class_index = Utils.read_uint16(ins)
        pair_count = Utils.read_uint16(ins)
        raw_size = Utils.read_uint32(ins)
        
        name = self.__class_names.get(class_index)
        class_def = ClassDefinition(class_index, name)
        class_def.raw_size = raw_size
        self.__data.register_class(class_def)

        for i in range(pair_count):
            default_val = Utils.read_uint32(ins)
            n = Utils.read_uint32(ins)
        num_references = Utils.read_vle(ins)
        for j in range(num_references):
            n = Utils.read_uint16(ins)
        num_offsets = Utils.read_vle(ins)
        for k in range(num_offsets):
            n = Utils.read_uint32(ins)
        num_offsets_indices = Utils.read_vle(ins)
        for l in range(num_offsets_indices):
            n = Utils.read_uint16(ins)
        return class_def
