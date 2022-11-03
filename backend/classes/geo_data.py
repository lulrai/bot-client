from backend.common.data_types import Position

class DidGeoData():
    def __init__(self, did: int) -> None:
        self.__did: int = did
        self.__geo: list[Position] = []

    @property
    def did(self) -> int:
        return self.__did
    @property
    def geo_positions(self) -> list[Position]:
        return self.__geo

    def add_geo_data(self, position: Position) -> None:
        self.__geo.append(position)

class AchievableGeoDataItem():
    def __init__(self, key: str, key2: str, did: int, position: Position) -> None:
        self.__key: str = key
        self.__key2: str = key2
        self.__did: int = did
        self.__position: Position = position

    @property
    def key(self) -> str:
        return self.__key
    @property
    def key2(self) -> str:
        return self.__key2
    @property
    def did(self) -> int:
        return self.__did
    @property
    def position(self) -> Position:
        return self.__position

class ContentLayerGeoData():
    def __init__(self, content_layer: int) -> None:
        self.__content_layer: int = content_layer
        self.__did_geodata: dict[int, DidGeoData] = {}

    @property
    def content_layer(self) -> int:
        return self.__content_layer
    @property
    def dids(self) -> list[int]:
        return list(self.__did_geodata.keys())
    @property
    def size(self) -> int:
        return len(self.__did_geodata)

    def add_geodata(self, geodata: DidGeoData) -> None:
        self.__did_geodata[geodata.did] = geodata

    def get_geodata(self, did: int) -> DidGeoData:
        return self.__did_geodata.get(did)

class AchievableGeoData():
    def __init__(self, achievable_id: int) -> None:
        self.__achievable_id: int = achievable_id
        self.__data: dict[int, dict[int, AchievableGeoData]] = {}

    @property
    def achievable_id(self) -> int:
        return self.__achievable_id
    @property
    def empty(self) -> bool:
        return len(self.__data.keys()) > 0

    def get_objective_indices(self) -> list[int]:
        return sorted(list(self.__data.keys()))

    def get_condition_indices(self, objective_index: int) -> list[int]:
        result: list[int] = []
        objective_data: dict[int, list[AchievableGeoDataItem]] = self.__data.get(objective_index)
        if objective_data:
            result.extend(list(objective_data.keys()))
            result.sort()
        return result

    def get_condition_data(self, objective_index: int, condition_index: int) -> list[AchievableGeoDataItem]:
        result: list[AchievableGeoDataItem] = []
        objective_data: dict[int, list[AchievableGeoDataItem]] = self.__data.get(objective_index)
        if objective_data:
            items: AchievableGeoDataItem = objective_data.get(condition_index)
            if items:
                result.append(items)
        return result

    def add_geodata(self, objective_index: int, condition_index: int, item: AchievableGeoDataItem) -> None:
        objective_data: dict[int, list[AchievableGeoDataItem]] = self.__data.get(objective_index)
        if objective_data is None:
            objective_data = {}
            self.__data[objective_index] = objective_data
        items: list[AchievableGeoDataItem] = objective_data.get(condition_index)
        if items is None:
            items: list[AchievableGeoDataItem] = []
            objective_data[condition_index] = items
        items.append(item)

    def get_all_items(self) -> list[AchievableGeoDataItem]:
        result: list[AchievableGeoDataItem] = []
        for objective_index in self.get_objective_indices():
            condition_indices: list[int] = self.get_condition_indices(objective_index)
            for condition_index in condition_indices:
                items: list[AchievableGeoDataItem] = self.get_condition_data(objective_index, condition_index)
                result.extend(items)
        return result

class GeoData():
    def __init__(self) -> None:
        self.__world_data: ContentLayerGeoData = ContentLayerGeoData(0)
        self.__content_layers_data: dict[int, ContentLayerGeoData] = {}
        self.__achievable_geodata: dict[int, AchievableGeoData] = {}

    def add_world_geodata(self, geodata: DidGeoData) -> None:
        self.__world_data.add_geodata(geodata)

    def add_content_layer_geodata(self, geodata: DidGeoData, content_layer: int) -> None:
        content_layer_geodata: ContentLayerGeoData = self.__content_layers_data.get(content_layer)
        if content_layer_geodata is None:
            content_layer_geodata = ContentLayerGeoData(content_layer)
            self.__content_layers_data[content_layer] = content_layer_geodata
        content_layer_geodata.add_geodata(geodata)

    def get_content_layers(self) -> list[int]:
        return sorted(list(self.__content_layers_data.keys()))

    def get_world_geodata(self) -> ContentLayerGeoData:
        return self.__world_data

    def add_geodata(self, geodata: AchievableGeoData) -> None:
        achievable_id: int = geodata.achievable_id
        if achievable_id in self.__achievable_geodata: print('Overriden geodata for achievale:', achievable_id)
        self.__achievable_geodata[achievable_id] = geodata

    def get_geodata_for_achievable(self, achievable_id: int) -> AchievableGeoData:
        return self.__achievable_geodata.get(achievable_id)

    def get_all_achievable_geodata(self) -> list[AchievableGeoData]:
        result: list[AchievableGeoData] = []
        achievable_keys: list[int] = sorted(list(self.__achievable_geodata.keys()))
        for achievable_key in achievable_keys:
            result.append(self.__achievable_geodata.get(achievable_key))
        return result