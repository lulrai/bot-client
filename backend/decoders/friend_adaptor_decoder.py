from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.config import GameConfig
from backend.decoders.properties_decoder import PropertiesDecoder

if TYPE_CHECKING:
    from backend.data_facade import DataFacade
    from backend.properties.properties_set import Properties

class FriendAdaptorDecoder():
    def __init__(self, config: GameConfig, data_facade: DataFacade) -> None:
        self.__config: GameConfig = config
        self.__props_decoder: PropertiesDecoder = PropertiesDecoder(config, data_facade)

    def handle_friend_adaptor(self, native_package_ptr: int, raw_size: int) -> Properties:
        return self.__props_decoder.handle_properties(native_package_ptr, self.__config.pointer_size)
