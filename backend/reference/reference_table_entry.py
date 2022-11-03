class ReferenceTableEntry():
    def __init__(self, index: int, package_id: int, bitfield: int, package_factory_info_ptr: int, wsl_package_ptr: int, native_package_ptr: int) -> None:
        self.__index: int = index
        self.__package_id: int = package_id
        self.__bitfield: int = bitfield
        self.__package_factory_info_ptr: int = package_factory_info_ptr
        self.__wsl_package_ptr: int = wsl_package_ptr
        self.__native_package_ptr: int = native_package_ptr

    @property
    def index(self) -> int:
        return self.__index
    @property
    def package_id(self) -> int:
        return self.__package_id
    @property
    def bitfield(self) -> int:
        return self.__bitfield
    @property
    def package_factory_info_ptr(self) -> int:
        return self.__package_factory_info_ptr
    @property
    def wsl_package_ptr(self) -> int:
        return self.__wsl_package_ptr
    @property
    def native_package_ptr(self) -> int:
        return self.__native_package_ptr