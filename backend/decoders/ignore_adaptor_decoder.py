from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import Config
from backend.decoders.properties_decoder import PropertiesDecoder
from backend.properties.properties_set import Properties

if TYPE_CHECKING:
    from backend.data_facade import DataFacade


class IgnoreAdaptorDecoder():
    def __init__(self, config: Config, data_facade: DataFacade) -> None:
        self.__config: Config = config
        self.__props_decoder: PropertiesDecoder = PropertiesDecoder(config, data_facade)

    def handle_ignore_adaptor(self, native_package_ptr: int, raw_size: int) -> Properties:
        return self.__props_decoder.handle_properties(native_package_ptr, self.__config.pointer_size)