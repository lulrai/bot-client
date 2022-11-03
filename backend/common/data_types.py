from __future__ import annotations

import io
import math
import struct
from typing import TYPE_CHECKING

from backend.managers.abstract_mappers import EnumMapper

if TYPE_CHECKING:
    from backend.common.config import Config

class Color:
    def __init__(self, r, g, b, a):
        self.r, self.g, self.b, self.a = r, g, b, a

    @classmethod
    def from_uint32(cls, val):
        a = val >> 24
        r = (val >> 16) & 255
        g = (val >> 8) & 255
        b = val & 255
        return cls(r, g, b, a)

    def __repr__(self):
        return f'Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})'

class Position:
    REGION = 0x01
    BLOCK = 0x02
    INSTANCE = 0x04
    CELL = 0x08
    POS = 0x10
    ROT = 0x20
    INHIBIT_REGION = 0x40
    INHIBIT_CELL = 0x80

    def __init__(self, flags, r, bx, by, instance, cell, offset, rot):
        self.flags = flags
        self.region = r
        self.bx = bx
        self.by = by
        self.instance = instance
        self.cell = cell
        self.pos = offset
        self.rot = rot

    @classmethod
    def make(cls, r=None, bx=None, by=None, instance=None, cell=None,
             pos=None, rot=None) -> Position:
        flags = 0
        if r is not None:
            flags |= Position.REGION
        if bx is not None:
            flags |= Position.BLOCK
        if by is not None:
            flags |= Position.BLOCK
        if instance is not None:
            flags |= Position.INSTANCE
        if cell is not None:
            flags |= Position.CELL
        if pos is not None:
            flags |= Position.POS
        if rot is not None:
            flags |= Position.ROT
        if r == 1:
            flags |= Position.INHIBIT_REGION  # inhibit region 1
        if cell is not None:
            flags |= Position.INHIBIT_CELL  # inhibit cell
        return cls(flags, r, bx, by, instance, cell, pos, rot)

    @classmethod
    def from_dat(cls, ins) -> Position:
        flags = struct.unpack('<b', ins.read(1))[0]
        region = 1
        bx = 0
        by = 0
        instance = 0
        cell = 0
        pos = None
        rot = None
        if flags & Position.REGION:
            region = struct.unpack('<b', ins.read(1))[0]
        if flags & Position.BLOCK:
            bx, by = ins.read(2)
        if flags & Position.INSTANCE:
            instance = struct.unpack('<H', ins.read(2))[0]
        if flags & Position.CELL:
            cell = struct.unpack('<H', ins.read(2))[0]
        if flags & Position.POS:
            pos = Vector3D(*struct.unpack('<3f', ins.read(12)))
        if flags & Position.ROT:
            rot = Quaternion(*struct.unpack('<4f', ins.read(16)))
        return cls(flags, region, bx, by, instance, cell, pos, rot)

    @classmethod
    def from_net(cls, ins) -> Position:
        flags = ord(ins.read(1))
        r = 1
        bx = 0
        by = 0
        i = 0
        c = 0
        offset = None
        rot = None
        if (flags & Position.REGION) and flags & Position.INHIBIT_REGION == 0:
            r = ord(ins.read(1))
        if flags & Position.BLOCK:
            bx, by = ins.read(2)
        if flags & Position.INSTANCE:
            i, = struct.unpack('<H', ins.read(2))
        if (flags & Position.CELL) and flags & Position.INHIBIT_CELL == 0:
            c, = struct.unpack('<H', ins.read(2))
        if flags & Position.POS:
            offset = Vector3D(*struct.unpack('<3f', ins.read(12)))
        if flags & Position.ROT:
            rot = Quaternion(*struct.unpack('<4f', ins.read(16)))
        return cls(flags, r, bx, by, i, c, offset, rot)

    @classmethod
    def from_mem(cls, config: Config, ptr: int, offset: int) -> Position:
        start_offset: int = offset + config.pointer_size
        pad: int = 6 if config.is_64bits else 2

        region: int = config.mem.read_uint((ptr+start_offset) + 0)
        bx: int = int.from_bytes(config.mem.read_bytes((ptr+start_offset) + 4), "little") & 0xFF
        by: int = int.from_bytes(config.mem.read_bytes((ptr+start_offset) + 5), "little") & 0xFF
        
        cell: int = int(config.mem.read_short((ptr+start_offset) + 6)) & 0xFFFF
        instance: int = int(config.mem.read_short((ptr+start_offset) + 8)) & 0xFFFF

        x: int = config.mem.read_float((ptr+start_offset) + 10 + pad)
        y: int = config.mem.read_float((ptr+start_offset) + 14 + pad)
        z: int = config.mem.read_float((ptr+start_offset) + 18 + pad)
        vec: Vector3D = Vector3D(x, y, z)

        q_w: int = config.mem.read_float((ptr+start_offset) + 22 + pad)
        q_x: int = config.mem.read_float((ptr+start_offset) + 24 + pad)
        q_y: int = config.mem.read_float((ptr+start_offset) + 28 + pad)
        q_z: int = config.mem.read_float((ptr+start_offset) + 32 + pad)
        quart: Quaternion = Quaternion(q_w, q_x, q_y, q_z)
        return cls.make(region, bx, by, instance, cell, vec, quart)

    def __repr__(self):
        parts = []
        if self.flags & Position.REGION and self.flags & Position.INHIBIT_REGION == 0:
            parts.append('r{}'.format(self.region))
        if self.flags & Position.BLOCK:
            parts.append('bx={:02X}, by={:02X}'.format(self.bx, self.by))
        if self.flags & Position.INSTANCE:
            parts.append('i={:04X}'.format(self.instance))
        if self.flags & Position.CELL and self.flags & Position.INHIBIT_CELL == 0:
            parts.append('c={:04X}'.format(self.cell))
        if self.flags & Position.POS:
            parts.append('pos={}'.format(self.pos))
        if self.flags & Position.ROT:
            parts.append('rot={}'.format(self.rot))
        return 'Position({})'.format(', '.join(parts))

    def __eq__(self, other):
        return self.region == other.region and \
               self.bx == other.bx and self.by == other.by and \
               self.cell == other.cell and \
               self.instance == other.instance and \
               self.pos == other.pos and self.rot == other.rot

class Vector3D:
    F_EPSILON = 0.0002

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def fmt_f(self, f):
        f1 = '{:.3f}'.format(f)
        while f1[-1] == '0' and f1[-2] != '.':
            f1 = f1[:-1]
        return f1

    def __eq__(self, other):
        return math.fabs(self.x - other.x) <= Vector3D.F_EPSILON and math.fabs(self.y - other.y) <= Vector3D.F_EPSILON and math.fabs(self.z - other.z) <= Vector3D.F_EPSILON

    def __repr__(self):
        return f'Vector3D({self.fmt_f(self.x)}, {self.fmt_f(self.y)}, {self.fmt_f(self.z)})'


class Quaternion:
    def __init__(self, w, x, y, z):
        self.w, self.x, self.y, self.z = w, x, y, z

    def fmt_f(self, f):
        f1 = '{:.3f}'.format(f)
        while f1[-1] == '0' and f1[-2] != '.':
            f1 = f1[:-1]
        return f1

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and \
            self.z == other.z and self.w == other.w

    def __repr__(self):
        return f'Quaternion(w=({self.fmt_f(self.w)}, {self.fmt_f(self.x)}, {self.fmt_f(self.y)}, {self.fmt_f(self.z)})'


class BitSet():
    ADDRESS_BITS_PER_WORD = 6
    BITS_PER_WORD = 1 << ADDRESS_BITS_PER_WORD
    BIT_INDEX_MASK = BITS_PER_WORD - 1
    WORD_MASK = 0xffffffffffffffff

    def __init__(self, words: list[int] = None, nbits: int = BITS_PER_WORD) -> None:
        if words:
            self.__words: list[int] = words
            self.__words_in_use = len(words)
            self.__check_invariants()
        else:
            self.__words_in_use = 0
            self.__size_is_sticky = nbits != BitSet.BITS_PER_WORD
            self.__words = [0] * (self.__word_index(nbits - 1) + 1)

    def __word_index(self, bit_index: int) -> int:
        return bit_index >> BitSet.ADDRESS_BITS_PER_WORD

    def __check_invariants(self) -> None:
        assert(self.__words_in_use == 0 or self.__words[self.__words_in_use - 1] != 0)
        assert(self.__words_in_use >= 0 and self.__words_in_use <= len(self.__words))
        assert(self.__words_in_use == len(self.__words) or self.__words[self.__words_in_use] == 0)

    def set(self, bit_index: int) -> None:
        assert bit_index >= 0
        word_index = self.__word_index(bit_index)
        if self.__words_in_use < word_index+1:
            if len(self.__words) < word_index+1:
                self.__words.extend(([0] * word_index+1))
            self.__words_in_use = word_index+1
        self.__words[word_index] = self.__words[word_index] | (1 << bit_index)
        self.__check_invariants()

    def get(self, bit_index: int) -> bool:
        assert bit_index >= 0
        self.__check_invariants()
        word_index = self.__word_index(bit_index)
        return (word_index < self.__words_in_use) and ((self.__words[word_index] & (1 << bit_index)) != 0)

    def get_string(self, enum_mapper: EnumMapper, seperator: str) -> str:
        if self.__words_in_use > 0:
            result_str = ''
            for i in range(self.__words_in_use):
                if self.get(i):
                    item_str = enum_mapper.get_string(i + 1)
                    if item_str is not None:
                        if len(result_str) > 0: 
                            result_str += seperator
                        result_str += item_str
            return result_str
        return None

    @classmethod
    def __read_vle(cls, ins):
        a = ord(ins.read(1))
        if a & 0x80 == 0:
            return a

        # Fishy but works (?)
        if a == 0xe0:
            return struct.unpack('<L', ins.read(4))[0]

        b = ord(ins.read(1))
        if a & 0x40 == 0x40:
            c, = struct.unpack('<H', ins.read(2))
            return (a & 0x3f) << 24 | b << 16 | c
        else:
            return b | ((a & 0x7f) << 8)

    @classmethod
    def from_stream(cls, ins: io.BytesIO, nb_bits: int = None) -> BitSet:
        num_bits = cls.__read_vle(ins) if nb_bits is None else nb_bits
        num_bytes = num_bits // 8
        if num_bits % 8 != 0:
            num_bytes += 1
        buffer = bytearray(ins.read(num_bytes))
        bit_set = cls()
        for i in range(num_bits):
            byte_idx = i // 8
            bit_idx = i % 8
            set_bool = ((ord(buffer[byte_idx]) & 1 << bit_idx) != 0 )
            if set_bool:
                bit_set.set(bit_idx)
        return bit_set

    @classmethod
    def from_bytearray(cls, buffer: bytearray, nb_bits: int) -> BitSet:
        bit_set = cls()
        for i in range(nb_bits):
            byte_idx = i // 8
            bit_idx = i % 8
            set_bool = ((ord(buffer[byte_idx]) & 1 << bit_idx) != 0 )
            if set_bool:
                bit_set.set(bit_idx)
        return bit_set

    @classmethod
    def from_flags(cls, bitset: int, is_long: bool = False) -> BitSet:
        length = 64 if is_long else 32
        bit_set = cls(nbits = length)
        mask = 1
        for i in range(1, length+1):
            if bitset & mask != 0:
                bit_set.set(i - 1)
            mask = mask << 1
        return bit_set
