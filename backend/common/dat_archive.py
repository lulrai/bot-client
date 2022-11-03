from __future__ import annotations

import io
import struct
import zlib

from backend.common.file_entry import DirectoryEntry, FileEntry


class DATArchive():
    # Fp denotes the filepath to the dat file
    def __init__(self, fp: str, debug: bool = False) -> None:
        self.__file = open(fp, 'rb')
        self.__file.seek(0x140) # Seek to the beginning of the header (should always begin with BT)
        self.__dirs: dict[int, DirectoryEntry] = {}
        self.__root_entry = None
        self.__block_size = 0
        self.__dat_pack_version = 0
        self.__debug = debug

    @property
    def file_input(self) -> io.FileIO:
        return self.__file
    @property
    def root_entry(self) -> DirectoryEntry:
        return self.__root_entry

    def open(self) -> None:
        root_offset = self.read_super_block()
        self.__root_entry = DirectoryEntry(None, root_offset)

    def close(self) -> None:
        self.__file.close()
    
    def read_directory(self, dir_entry: DirectoryEntry) -> None:
        offset = dir_entry.offset
        if self.__debug: print(f'Reading directory at offset: {offset}')
        self.__file.seek(offset)
        num_extra_blocks, legacy = struct.unpack('<2L', self.__file.read(8))
        self.__file.seek(offset + 0x1f8)
        files_count, = struct.unpack('<L', self.__file.read(4))
        self.__file.seek(offset + 0x8)
        for i in range(files_count+1):
            block_size, dir_offset = struct.unpack('<2L', self.__file.read(8))
            if block_size:
                if self.__debug: print(f'Dir entry #{i}: got block_size = {block_size}, offset = {dir_offset}')
                d_entry = DirectoryEntry(dir_entry, dir_offset)
                dir_entry.add_dir(d_entry)
        if self.__debug: print(f'Got {len(dir_entry.dirs)} directories!')
        if self.__debug: print(f'Expect {files_count} files!')
        self.__file.seek(offset + 0x1f8 + 0x4)
        for j in range(files_count):
            flags, policy = struct.unpack('<2h', self.__file.read(4))
            file_id, file_offset, size = struct.unpack('<3L', self.__file.read(12))
            timestamp, version, file_block_size = struct.unpack('<3L', self.__file.read(12))
            self.__file.read(4)
            entry = FileEntry(j, file_id, file_offset, version, timestamp, size, file_block_size, flags, policy)
            if self.__debug: print(f'File entry: Index = {entry.index}, file_id = {hex(entry.file_id)}, file_offset = {entry.file_offset},', 
            f'version = {entry.version}, timestamp = {entry.timestamp}, size = {entry.size}, block_size = {entry.block_size}, flags = {entry.flags}, policy = {entry.policy}'
            )
            dir_entry.add_file(entry)


    def read_super_block(self) -> int:
        header_bytes = self.__file.read(0x68) # Read the next 68 bytes of header information

        ins = io.BytesIO(header_bytes) # Read the whole header as bytes for IO
        magic, = struct.unpack('<L', ins.read(4)) # Get the first 4 bytes of type "<L" (long = 4 bytes and "<" represents little endian the order to read the bytes)
        if magic != 0x5442: # Check if it matches the byte format: 00 00 42 54 (bytes) or 0x5242 (hex) or 21570 (dec) signifying the beginning
            raise Exception('bad datfile header check') # If not, then just error
        
        self.__block_size, = struct.unpack('<L', ins.read(4)) # Read 4 bytes after the magic bytes, that's the block size
        ins.read(0x18) # Seek 24 bytes to reach the root node offset which is what we need

        root_node_offset, = struct.unpack('<L', ins.read(4)) # Read 4 bytes after seeking, that's root node of the btree (IMPORTANT)
        ins.read(0x10) # Seek 16 bytes to reach the dat pack verson

        self.__dat_pack_version, = struct.unpack('<L', ins.read(4)) # Read 4 bytes after seeking, that's dat pack version, can be useful while parsing
        ins.close()
        return root_node_offset

    def load_entry(self, file_entry: FileEntry) -> bytearray:
        offset = file_entry.file_offset
        self.__file.seek(offset)
        num_extra_blocks, legacy = struct.unpack('<2L', self.__file.read(8))
        first_chunk_size = file_entry.block_size - 8 - num_extra_blocks * 8
        first_chunk_size = first_chunk_size if first_chunk_size <= file_entry.size else file_entry.size
        data = bytearray(self.__file.read(first_chunk_size))
        block_links = [struct.unpack('<2L', self.__file.read(8))
                    for _ in range(num_extra_blocks)]
        for size, offset in block_links:
            self.__file.seek(offset)
            data.extend(self.__file.read(size))
        total_size = file_entry.size
        if len(data) > total_size:
            data = data[:total_size]
        if file_entry.is_compressed:
            mv = memoryview(data)
            decompressed_size = int.from_bytes(mv[:4], 'little')
            data = zlib.decompress(mv[4:],
                                   zlib.MAX_WBITS,
                                   decompressed_size)
            if len(data) != decompressed_size:
                raise Exception('decompressed data size mismatch')
        return data

    def load_entry_by_id(self, file_id: int) -> bytearray:
        entry = self.__find_file_by_id(self.__root_entry, file_id)
        if entry:
            return self.load_entry(entry)

    def __ensure_loaded_dir(self, dir_entry: DirectoryEntry):
        offset = dir_entry.offset
        if offset not in self.__dirs:
            self.read_directory(dir_entry)
            self.__dirs[offset] = dir_entry

    def __find_file_by_id(self, dir: DirectoryEntry, fileId: int) -> FileEntry:
        if self.__debug: print('Dir entry for get file:', dir.offset)
        self.__ensure_loaded_dir(dir)
        files = dir.files
        lower = 0
        upper = len(files) - 1
        while lower <= upper:
            possible = (lower+upper)//2
            file_entry: FileEntry = files[possible]
            if self.__debug: print(f"u: {upper}, l: {lower}, p: {possible}, current_file_id: {file_entry.file_id}, given_file_id: {fileId}, is_smaller: {file_entry.file_id < fileId}")
            if file_entry.file_id < fileId:
                lower = possible + 1
            elif file_entry.file_id > fileId:
                upper = possible - 1
            else:
                return file_entry
        dir_entries = dir.dirs
        if len(dir_entries) > 0:
            sub_dir = dir_entries[lower]
            return self.__find_file_by_id(sub_dir, fileId)
        return None
