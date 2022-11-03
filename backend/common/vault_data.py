from backend.properties.properties_set import Properties, PropertyValue

class VaultItemDescriptor():
    def __init__(self, itemIID: int, props: Properties, tooltip_helper: PropertyValue) -> None:
        self.__itemIID: int = itemIID
        self.__props: Properties = props
        self.__tooltip_helper: PropertyValue = tooltip_helper

    @property
    def itemIID(self) -> int:
        return self.__itemIID
    @property
    def ownerIID(self) -> int:
        return self.__props.get_property('Bank_Repository_ItemManagerIID')
    @property
    def bank_type(self) -> int:
        return self.__props.get_property('BankRepository_BankType')
    @property
    def props(self) -> Properties:
        return self.__props
    @property
    def tooltip_helper(self) -> PropertyValue:
        return self.__tooltip_helper

class VaultDescriptor():
    def __init__(self) -> None:
        self.__current_quantity: int = 0
        self.__max_capacity: int = 0
        self.__chest_names: dict[int, str] = {}

    @property
    def current_quantity(self) -> int:
        return self.__current_quantity
    @property
    def max_capacity(self) -> int:
        return self.__max_capacity

    def add_chest(self, chest_id: int, name: str) -> None:
        self.__chest_names[chest_id] = name

    def set_state(self, current_quantity: int, max_capacity: int) -> None:
        self.__current_quantity = current_quantity
        self.__max_capacity = max_capacity

    def get_chest_ids(self) -> list[int]:
        return sorted(list(self.__chest_names.keys()))

    def get_chest_name(self, chest_id: int) -> str:
        return self.__chest_names.get(chest_id)