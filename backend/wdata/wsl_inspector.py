from backend.reference.reference_table_controller import ReferencesTableController, ReferenceTableEntry
from backend.classes.class_definition import ClassInstance
from backend.reference.reference_provider import ReferencesTableReferenceProvider
from backend.reference.reference_resolver import ReferencesResolver

class WSLInspector():
    def __init__(self, references_table_controller: ReferencesTableController) -> None:
        self.__references_table_controller: ReferencesTableController = references_table_controller
        self.__provider: ReferencesTableReferenceProvider = ReferencesTableReferenceProvider(references_table_controller)

    def find_local_player(self) -> ClassInstance:
        table_size: int = self.__references_table_controller.table_size
        for i in range(table_size):
            entry: ReferenceTableEntry = self.__references_table_controller.get_entry(i)
            if entry:
                entry_package_id: int = entry.package_id
                if entry_package_id == 1654:
                    player_avatar: ClassInstance = self.__references_table_controller.get_value(i)
                    ref: int = player_avatar.get_attr_val('m_rcPedigreeRegistry') if player_avatar else None
                    if ref and ref >= 0:
                        self.__resolve(player_avatar)
                        return player_avatar
        return None

    def find_all(self, package_id: int) -> list[object]:
        result: list[object] = []
        table_size: int = self.__references_table_controller.table_size
        for i in range(table_size):
            entry: ReferenceTableEntry = self.__references_table_controller.get_entry(i)
            if entry:
                entry_package_id: int = entry.package_id
                if entry_package_id == package_id:
                    value: object = self.__references_table_controller.get_value(i)
                    if isinstance(value, ClassInstance):
                        class_ins: ClassInstance = value
                        self.__resolve(class_ins)
                    result.append(value)
        return result

    def __resolve(self, resolve_obj: object) -> None:
        resolver: ReferencesResolver = ReferencesResolver(self.__provider)
        resolver.resolve_references_in_val(resolve_obj)
        to_resolve: list[object] = self.__provider.get_object_stacks_to_resolve()
        while len(to_resolve) > 0:
            obj_to_resolve: object = to_resolve.pop()
            resolver.resolve_references_in_val(obj_to_resolve)