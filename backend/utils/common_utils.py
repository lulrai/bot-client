"""Module containing common utility functions for R/W memory."""
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
    """Class that contains utility methods."""
    @staticmethod
    def retrieve_string(mem: pymem, read_addr: int, approx_read: int = 100) -> str:
        """
        Function to retrieve a string from memory.
        param mem: pymem object
        type mem: pymem.Pymem
        param read_addr: address to read from
        type read_addr: int
        param approx_read: approximate number of bytes to read
        type approx_read: int
        returns: string
        rtype: str
        """
        eol_pattern = b"\x00\x00\x00[ .]*[\x00]*"
        search_result = re.search(eol_pattern, mem.read_bytes(read_addr, approx_read))
        if search_result:
            return mem.read_bytes(read_addr, search_result.start()).replace(b'\x00', b'').decode("utf-8", errors='ignore')
        return ''

    @staticmethod
    def read_arb_bitfield(config: Config, bit_field_ptr: int, offset: int) -> BitSet:
        """
        Function to read an arbitrary bitfield.
        param config: config object
        type config: Config
        param bit_field_ptr: address of the bitfield
        type bit_field_ptr: int
        param offset: offset of the bitfield
        type offset: int
        returns: BitSet
        rtype: BitSet
        """
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
        """
        Function to read an arbitrary bitfield from a stream.
        param ins: input stream
        type ins: io.BytesIO
        returns: BitSet
        rtype: BitSet
        """
        bit_count = Utils.read_vle(ins)
        if bit_count == 0: return BitSet()
        byte_count = bit_count // 8 + (bit_count % 8 != 0)
        ret = BitSet(nbits=bit_count)
        bit_index = 0
        for _ in range(byte_count):
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
        """
        Function to get a string property.
        param propeties: properties object
        type propeties: Properties
        param property_name: name of the property
        type property_name: str
        returns: string
        rtype: str
        """
        value = propeties.get_property(property_name)
        result: str = ''
        if value:
            if isinstance(value, str): result = value
            else: print('Unsupported property value class:', type(value))
            return result.replace('\\n', '\n').strip()
        return None

    @staticmethod
    def read_raw_chunk(ins: io.BytesIO) -> bytes:
        """
        Function to read a raw chunk.
        param ins: input stream
        type ins: io.BytesIO
        returns: bytes
        rtype: bytes
        """
        size, = struct.unpack('<L', ins.read(4))
        return ins.read(size)

    @staticmethod
    def read_vle_old(ins: io.BytesIO) -> int:
        """
        Function to read a VLE. (old version)
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        result = ord(ins.read(1))
        if result & 0x80:
            b = ord(ins.read(1))
            result = ((result & 0x7f) << 8) | b
        if result == 0x4000:
            return Utils.read_uint16(ins)
        else:
            return result

    @staticmethod
    def read_vle(ins: io.BytesIO) -> int:
        """
        Function to read a VLE. (new version)
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
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
        return b | ((a & 0x7f) << 8)
          
    @staticmethod
    def read_tsize(ins: io.BytesIO) -> int:
        """
        Reads the table size where the first value is an implementation detail: bucket count.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        ins.read(1)
        return Utils.read_vle(ins)

    @staticmethod
    def read_packed_enum(ins: io.BytesIO) -> int:
        """
        Reads a packed enum.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        top = ord(ins.read(1))
        remainder = Utils.read_vle(ins)
        return (top << 24) | remainder

    @staticmethod
    def read_int64(ins: io.BytesIO) -> int:
        """
        Function to read a 64-bit integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<q', ins.read(8))[0]
    
    @staticmethod
    def read_uint64(ins: io.BytesIO) -> int:
        """
        Function to read a 64-bit unsigned integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<Q', ins.read(8))[0]

    @staticmethod
    def read_uint32(ins: io.BytesIO) -> int:
        """
        Function to read a 32-bit unsigned integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<L', ins.read(4))[0]

    @staticmethod
    def read_int32(ins: io.BytesIO) -> int:
        """
        Function to read a 32-bit integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<l', ins.read(4))[0]

    @staticmethod
    def read_uint16(ins: io.BytesIO) -> int:
        """
        Function to read a 16-bit unsigned integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<H', ins.read(2))[0]

    @staticmethod
    def read_int16(ins: io.BytesIO) -> int:
        """
        Function to read a 16-bit integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<h', ins.read(2))[0]

    @staticmethod
    def read_uint8(ins: io.BytesIO) -> int:
        """
        Function to read a 8-bit unsigned integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<B', ins.read(1))[0]

    @staticmethod
    def read_int8(ins: io.BytesIO) -> int:
        """
        Function to read a 8-bit integer.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        return struct.unpack('<b', ins.read(1))[0]

    @staticmethod
    def read_float(ins: io.BytesIO) -> float:
        """
        Function to read a float.
        param ins: input stream
        type ins: io.BytesIO
        returns: float
        rtype: float
        """
        return struct.unpack('<f', ins.read(4))[0]

    @staticmethod
    def read_double(ins: io.BytesIO) -> float:
        """
        Function to read a double.
        param ins: input stream
        type ins: io.BytesIO
        returns: float
        rtype: float
        """
        return struct.unpack('<d', ins.read(8))[0]

    @staticmethod
    def read_ascii_string(ins: io.BytesIO) -> str:
        """
        Function to read an ASCII string.
        param ins: input stream
        type ins: io.BytesIO
        returns: str
        rtype: str
        """
        length = ins.read(1)
        return ins.read(length).decode('ascii')

    @staticmethod
    def read_pascal_string(ins: io.BytesIO) -> str:
        """
        Function to read a Pascal string.
        param ins: input stream
        type ins: io.BytesIO
        returns: str
        rtype: str
        """
        length = Utils.read_vle(ins)
        return ins.read(length).decode('latin-1')

    @staticmethod
    def read_prefixed_utf16(ins: io.BytesIO) -> str:
        """
        Function to read a UTF-16 string.
        param ins: input stream
        type ins: io.BytesIO
        returns: str
        rtype: str
        """
        length = Utils.read_vle(ins)
        return ins.read(length * 2).decode('utf-16')

    @staticmethod
    def read_wave(ins: io.BytesIO) -> tuple[int, list[float]]:
        """
        Function to read a wave.
        param ins: input stream
        type ins: io.BytesIO
        returns: tuple[int, list[float]]
        rtype: tuple[int, list[float]]
        """
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
    def peek(ins: io.BytesIO, datatype: str) -> int:
        """
        Function to peek at the next byte.
        param ins: input stream
        type ins: io.BytesIO
        param datatype: data type
        type datatype: str
        returns: int
        rtype: int
        """
        size = struct.calcsize(datatype)
        val, = struct.unpack(f'<{datatype}', ins.read(size))
        ins.seek(-size, io.SEEK_CUR)
        return val

    @staticmethod
    def skip(ins: io.BytesIO, delta: int) -> None:
        """
        Function to skip a number of bytes.
        param ins: input stream
        type ins: io.BytesIO
        param delta: number of bytes to skip
        type delta: int
        returns: None
        rtype: None
        """
        ins.seek(delta, io.SEEK_CUR)

    @staticmethod
    def read_color(ins: io.BytesIO) -> Color:
        """
        Function to read a color.
        param ins: input stream
        type ins: io.BytesIO
        returns: Color
        rtype: Color
        """
        r, g, b, a = ins.read(4)
        return Color(r, g, b, a)

    @staticmethod
    def fmt_f(f: float) -> str:
        """
        Function to format a float.
        param f: float
        type f: float
        returns: str
        rtype: str
        """
        f1 = '{:.3f}'.format(f)
        while f1[-1] == '0' and f1[-2] != '.':
            f1 = f1[:-1]
        return f1
        
    @staticmethod
    def feq(a: float, b: float) -> bool:
        """
        Function to compare two floats.
        param a: float
        type a: float
        param b: float
        type b: float
        returns: bool
        rtype: bool
        """
        F_EPSILON = 0.0002
        return math.fabs(a - b) <= F_EPSILON

    @staticmethod
    def read_vector3d(ins: io.BytesIO) -> Vector3D:
        """
        Function to read a vector3d.
        param ins: input stream
        type ins: io.BytesIO
        returns: Vector3D
        rtype: Vector3D
        """
        return Vector3D(*struct.unpack('<3f', ins.read(12)))

    @staticmethod
    def read_quaternion(ins: io.BytesIO) -> Quaternion:
        """
        Function to read a quaternion.
        param ins: input stream
        type ins: io.BytesIO
        returns: Quaternion
        rtype: Quaternion
        """
        return Quaternion(*struct.unpack('<4f', ins.read(16)))

    @staticmethod
    def read_bool(ins: io.BytesIO) -> bool:
        """
        Function to read a boolean.
        param ins: input stream
        type ins: io.BytesIO
        returns: bool
        rtype: bool
        """
        val = ord(ins.read(1))
        if val == 0:
            return False
        elif val == 1:
            return True
        else:
            raise ValueError('Bad bool value {:02X}'.format(val))

    @staticmethod
    def read_prefixed_array(ins: io.BytesIO, lentype: str, valtype: str) -> list:
        """
        Function to read a prefixed array.
        param ins: input stream
        type ins: io.BytesIO
        param lentype: length type
        type lentype: str
        param valtype: value type
        type valtype: str
        returns: list
        rtype: list
        """
        length, = struct.unpack(f'<{lentype}', ins.read(struct.calcsize(lentype)))
        return struct.unpack(f'<{length}{valtype}', ins.read(length * struct.calcsize(valtype)))

    @staticmethod
    def bytes_available(ins: io.BytesIO) -> int:
        """
        Function to check how many bytes are available.
        param ins: input stream
        type ins: io.BytesIO
        returns: int
        rtype: int
        """
        current_pos = ins.tell()
        ins.seek(0, 2)
        length = ins.tell()
        ins.seek(current_pos, 0)
        return length-current_pos

    @staticmethod
    def hash(string: str) -> int:
        """
        Function to hash a string.
        param string: string
        type string: str
        returns: int
        rtype: int
        """
        h = 0
        for ch in string:
            h = (h << 4) + ord(ch)
            hi = h & 0xf0000000
            h ^= hi >> 24
        h &= 0x0fffffff
        return h
