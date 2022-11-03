import io

from backend.common.data_types import Position
from backend.managers.knownvariables_manager import KnownVariablesManager
from backend.properties.properties_type import PropertyType
from backend.strings.string_info import (LiteralStringInfo, StringInfo,
                                         TableEntryStringInfo)
from backend.utils.common_utils import Utils


class PropertiesUtils():
    @staticmethod
    def read_property_value(ins: io.BytesIO, property_type: PropertyType) -> object:
        # property_type = property_type.val
        if (property_type == PropertyType.String): return PropertiesUtils.read_string(ins)
        if (property_type == PropertyType.StringToken): return PropertiesUtils.read_string_token(ins) 
        if (property_type == PropertyType.Waveform): return PropertiesUtils.read_waveform(ins) 
        if (property_type == PropertyType.TimeStamp): return PropertiesUtils.read_time_stamp(ins) 
        if (property_type == PropertyType.TriState): return PropertiesUtils.read_tristate(ins) 
        if (property_type == PropertyType.Vector): return PropertiesUtils.read_vector(ins) 
        if (property_type == PropertyType.InstanceID): return PropertiesUtils.read_instance_id(ins) 
        if (property_type == PropertyType.EnumMapper): return PropertiesUtils.read_enum_mapper(ins) 
        if (property_type == PropertyType.Float): return PropertiesUtils.read_float_value(ins) 
        if (property_type == PropertyType.PropertyID): return PropertiesUtils.read_property_id(ins)
        if (property_type == PropertyType.Struct): return PropertiesUtils.read_struct(ins) 
        if (property_type == PropertyType.Array): return PropertiesUtils.read_array(ins) 
        if (property_type == PropertyType.StringInfo): return PropertiesUtils.read_string_info(ins) 
        if (property_type == PropertyType.Bitfield64): return PropertiesUtils.read_bitfield_64(ins) 
        if (property_type == PropertyType.Int): return PropertiesUtils.read_int(ins) 
        if (property_type == PropertyType.Color): return PropertiesUtils.read_color(ins) 
        if (property_type == PropertyType.Position): return PropertiesUtils.read_position(ins) 
        if (property_type == PropertyType.Bitfield32): return PropertiesUtils.read_bitfield_32(ins) 
        if (property_type == PropertyType.Int64): return PropertiesUtils.read_int64(ins) 
        if (property_type == PropertyType.DataFile): return PropertiesUtils.read_datafile(ins) 
        if (property_type == PropertyType.Bool): return PropertiesUtils.read_bool(ins) 
        if (property_type == PropertyType.Bitfield): return PropertiesUtils.read_arbitrary_bitfield(ins) 
        print("Unmanaged property type: ", property_type)
        return None

    @staticmethod
    def read_string(ins):
        return Utils.read_pascal_string(ins)

    @staticmethod
    def read_string_token(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_waveform(ins):
        return Utils.read_wave(ins)

    @staticmethod
    def read_time_stamp(ins):
        return Utils.read_double(ins)

    @staticmethod
    def read_tristate(ins):  # 0xff is third state
        return Utils.read_uint8(ins)

    @staticmethod
    def read_vector(ins):
        return Utils.read_vector3d(ins)

    @staticmethod
    def read_instance_id(ins):
        return Utils.read_uint64(ins)

    @staticmethod
    def read_enum_mapper(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_float_value(ins):
        return Utils.read_float(ins)

    @staticmethod
    def read_property_id(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_struct(ins):
        return Utils.read_tsize(ins)

    @staticmethod
    def read_array(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_string_info(ins):
        str_info: StringInfo = None
        is_literal: bool = Utils.read_bool(ins)
        if is_literal:
            literal = Utils.read_prefixed_utf16(ins)
            return LiteralStringInfo(literal)
        else:
            token, data_id = Utils.read_uint32(ins), Utils.read_uint32(ins)
            str_info = TableEntryStringInfo(data_id, token)
        has_strings = Utils.read_bool(ins)
        if has_strings:
            dev_strings = [Utils.read_pascal_string(ins) for _ in range(3)]
            num_variables = Utils.read_vle(ins)
            for i in range(num_variables):
                vartype = Utils.read_int8(ins)
                if vartype not in (0, 1, 2, 4):
                    raise ValueError('New StringInfoRendering_VarType {}'.format(vartype))
                if vartype == 0:
                    continue
                variable_token = Utils.read_uint32(ins)
                variable_name = KnownVariablesManager().get_variable_from_hash(variable_token)
                if vartype != 1:
                    is1 = Utils.read_int8(ins)  # number of values?
                    if is1 != 1:
                        raise ValueError('New StringInfo is1 {}'.format(is1))
                if vartype == 4:  # Integer
                    val = Utils.read_vle(ins)
                    str_info.add_variable_value(variable_name, val)
                elif vartype == 1:  # String
                    val = PropertiesUtils.read_string_info(ins)
                    str_info.add_variable_value(variable_name, val)
                elif vartype == 2:  # Float
                    val = Utils.read_float(ins)
                    str_info.add_variable_value(variable_name, val)
        else:
            remainder1 = Utils.read_int8(ins)
            remainder2 = Utils.read_uint8(ins)
            assert remainder1 == 1 and remainder2 == 0
        return str_info        

    @staticmethod
    def read_bitfield_64(ins):
        return Utils.read_uint64(ins)
            
    @staticmethod
    def read_int(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_color(ins):
        return [n for n in ins.read(4)]

    @staticmethod
    def read_bitfield_32(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_position(ins):
        return Position.from_dat(ins)

    @staticmethod
    def read_int64(ins):
        return Utils.read_int64(ins)

    @staticmethod
    def read_bool(ins):
        return Utils.read_uint8(ins) == 1

    @staticmethod
    def read_datafile(ins):
        return Utils.read_uint32(ins)

    @staticmethod
    def read_arbitrary_bitfield(ins):
        return Utils.read_arb_bitfield_stream(ins)
