from __future__ import annotations

import io
import math
import re
import struct
from typing import TYPE_CHECKING

import pymem

from backend.common.data_types import BitSet, Color, Quaternion, Vector3D
from backend.properties.properties_set import Properties

if TYPE_CHECKING:
    from backend.common.config import Config

class Utils():
    @staticmethod
    def retrieve_string(mem: pymem, read_addr: int, approx_read: int = 80) -> str:
        EOL_pattern = b"\x00\x00\x00[ .]*[\x00]*"
        num_bytes = re.search(EOL_pattern, mem.read_bytes(read_addr, approx_read)).start()
        found_string = mem.read_bytes(read_addr, num_bytes).replace(b'\x00', b'').decode("utf-8", errors='ignore')
        return found_string

    @staticmethod
    def read_arb_bitfield(config: Config, bit_field_ptr: int, offset: int) -> BitSet:
        bit_count = config.mem.read_uint(bit_field_ptr+offset+config.pointer_size)
        if bit_count == 0: return BitSet()
        print('Nb bits:', bit_count)
        byte_count = bit_count // 8 + (bit_count % 8 != 0)
        ret = BitSet(nbits=bit_count)
        bit_index = 0
        for i in range(byte_count):
            value = ord(config.mem.read_bytes(bit_field_ptr+i, 1))
            local_bit_flag = 1
            while bit_index < bit_count and local_bit_flag < 256:
                if (value & local_bit_flag) != 0:
                    ret.set(bit_index)
                local_bit_flag *= 2
                bit_index += 1
        return ret    

    @staticmethod
    def read_arb_bitfield_stream(ins: io.BytesIO) -> BitSet:
        bit_count = Utils.read_vle(ins)
        if bit_count == 0: return BitSet()
        byte_count = bit_count // 8 + (bit_count % 8 != 0)
        ret = BitSet(nbits=bit_count)
        bit_index = 0
        for i in range(byte_count):
            value = Utils.read_uint8(ins)
            local_bit_flag = 1
            while bit_index < bit_count and local_bit_flag < 256:
                if (value & local_bit_flag) != 0:
                    ret.set(bit_index)
                local_bit_flag *= 2
                bit_index += 1
        return ret    

    @staticmethod
    def get_string_property(propeties: Properties, property_name: str) -> str: 
        value = propeties.get_property(property_name)
        result: str = ''
        if value:
            if isinstance(value, str): result = value
            else: print('Unsupported property value class:', type(value))
            return result.replace('\\n', '\n').strip()
        return None

    @staticmethod
    def read_raw_chunk(ins):
        size, = struct.unpack('<L', ins.read(4))
        return ins.read(size)

    @staticmethod
    def read_vle_old(ins):
        result = ord(ins.read(1))
        if result & 0x80:
            b = ord(ins.read(1))
            result = ((result & 0x7f) << 8) | b
        if result == 0x4000:
            return Utils.read_uint16(ins)
        else:
            return result

    @staticmethod
    def read_vle(ins):
        a = ord(ins.read(1))
        if a & 0x80 == 0:
            return a

        # Fishy but works (?)
        if a == 0xe0:
            return Utils.read_uint32(ins)

        b = ord(ins.read(1))
        if a & 0x40 == 0x40:
            c, = struct.unpack('<H', ins.read(2))
            return (a & 0x3f) << 24 | b << 16 | c
        else:
            return b | ((a & 0x7f) << 8)
            
    @staticmethod
    def read_tsize(ins):
        """
        The first value is an implementation detail: bucket count.

        """
        ins.read(1)
        return Utils.read_vle(ins)

    @staticmethod
    def read_packed_enum(ins):
        top = ord(ins.read(1))
        remainder = Utils.read_vle(ins)
        return (top << 24) | remainder

    @staticmethod
    def read_int64(ins):
        return struct.unpack('<q', ins.read(8))[0]
    
    @staticmethod
    def read_uint64(ins):
        return struct.unpack('<Q', ins.read(8))[0]

    @staticmethod
    def read_uint32(ins):
        return struct.unpack('<L', ins.read(4))[0]

    @staticmethod
    def read_int32(ins):
        return struct.unpack('<l', ins.read(4))[0]

    @staticmethod
    def read_uint16(ins):
        return struct.unpack('<H', ins.read(2))[0]

    @staticmethod
    def read_int16(ins):
        return struct.unpack('<h', ins.read(2))[0]

    @staticmethod
    def read_uint8(ins):
        return struct.unpack('<B', ins.read(1))[0]

    @staticmethod
    def read_int8(ins):
        return struct.unpack('<b', ins.read(1))[0]

    @staticmethod
    def read_float(ins):
        return struct.unpack('<f', ins.read(4))[0]

    @staticmethod
    def read_double(ins):
        return struct.unpack('<d', ins.read(8))[0]

    @staticmethod
    def read_ascii_string(ins):
        length = ins.read(1)
        return ins.read(length).decode('ascii')

    @staticmethod
    def read_pascal_string(ins):
        length = Utils.read_vle(ins)
        return ins.read(length).decode('latin-1')

    @staticmethod
    def read_prefixed_utf16(ins):
        length = Utils.read_vle(ins)
        return ins.read(length * 2).decode('utf-16')

    @staticmethod
    def read_wave(ins):
        type_wave = Utils.read_int32(ins)
        value = 0
        if type_wave == 1:
            value = Utils.read_float(ins)
        elif type_wave > 1:
            value = [0] * 10
            for i in range(10):
                value[i] = Utils.read_float(ins)
        return (type_wave, value)

    @staticmethod
    def peek(ins, datatype):
        size = struct.calcsize(datatype)
        val, = struct.unpack('<{}'.format(datatype), ins.read(size))
        ins.seek(-size, io.SEEK_CUR)
        return val

    @staticmethod
    def skip(ins, delta):
        ins.seek(delta, io.SEEK_CUR)

    @staticmethod
    def read_color(ins):
        r, g, b, a = ins.read(4)
        return Color(r, g, b, a)

    @staticmethod
    def fmt_f(f):
        f1 = '{:.3f}'.format(f)
        while f1[-1] == '0' and f1[-2] != '.':
            f1 = f1[:-1]
        return f1
        
    @staticmethod
    def feq(a, b):
        F_EPSILON = 0.0002
        return math.fabs(a - b) <= F_EPSILON

    @staticmethod
    def read_vector3d(ins):
        return Vector3D(*struct.unpack('<3f', ins.read(12)))

    @staticmethod
    def read_quaternion(ins):
        return Quaternion(*struct.unpack('<4f', ins.read(16)))

    @staticmethod
    def read_bool(ins):
        val = ord(ins.read(1))
        if val == 0:
            return False
        elif val == 1:
            return True
        else:
            raise ValueError('Bad bool value {:02X}'.format(val))

    @staticmethod
    def read_prefixed_array(ins, lentype, valtype):
        length, = struct.unpack('<{}'.format(lentype),
                                ins.read(struct.calcsize(lentype)))
        return struct.unpack('<{}{}'.format(length, valtype),
                            ins.read(length * struct.calcsize(valtype)))

    @staticmethod
    def bytes_available(ins):
        current_pos = ins.tell()
        ins.seek(0, 2)
        length = ins.tell()
        ins.seek(current_pos, 0)
        return length-current_pos

    @staticmethod
    def hash(string: str) -> int:
        h = 0
        for ch in string:
            h = (h << 4) + ord(ch)
            hi = h & 0xf0000000
            h ^= hi >> 24
        h &= 0x0fffffff
        return h
