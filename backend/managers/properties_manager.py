import io

from backend.properties.properties_def import PropertyDef
from backend.properties.properties_type import PropertyType
from backend.utils.common_utils import Utils
from backend.utils.prop_utils import PropertiesUtils


class PropertiesRegistry():
    properties: dict[int, PropertyDef] = {}
    props_by_name: dict[str, PropertyDef] = {}

    def register(self, prop_def: PropertyDef) -> None:
        self.properties[prop_def.pid] = prop_def
        self.props_by_name[prop_def.name] = prop_def

    def get_property_def(self, property_id: int) -> PropertyDef:
        return self.properties[property_id]

    def get_property_def_by_name(self, name: str) -> PropertyDef:
        return self.props_by_name[name]

    def get_property_ids(self) -> list[PropertyDef]:
        ids = list(self.properties.keys())
        ids.sort()
        return ids
        
class PropertyDefinitionsLoader():
    @staticmethod
    def read_property_value(ins, property_type: PropertyType, flags: int) -> object:
        property_type = property_type.val
        if (property_type == PropertyType.PropertyID):
            return None
        if (property_type == PropertyType.Struct):
            return None
        if (property_type == PropertyType.Array):
            return None 
        if (property_type == PropertyType.Position):
            return None
        return PropertiesUtils.read_property_value(ins, property_type)
        
    @staticmethod
    def read_property_def(ins: io.BytesIO, expected_pid: int, registry: PropertiesRegistry):
        prop_def: PropertyDef = registry.get_property_def(expected_pid)
        pid = Utils.read_uint32(ins)
        property_type_code = Utils.read_uint32(ins)
        prop_def.ptype = PropertyType(property_type_code)
        Utils.read_uint32(ins)
        Utils.read_uint32(ins)
        prop_def.data = Utils.read_uint32(ins)
        Utils.read_uint32(ins)

        v5 = Utils.read_uint32(ins)
        flags = v5 >> 8 & 0xFF
        if (v5 & 0x800) != 0:
            prop_def.def_val = PropertyDefinitionsLoader.read_property_value(ins, prop_def.ptype, flags)
        if (v5 & 0x1000) != 0:
            prop_def.min_val = PropertyDefinitionsLoader.read_property_value(ins, prop_def.ptype, flags)
        if (v5 & 0x2000) != 0:
            prop_def.max_val = PropertyDefinitionsLoader.read_property_value(ins, prop_def.ptype, flags)

        marker = Utils.read_uint32(ins)
        if marker != 1069547520:
            print('Bad property def and marker. Got', marker)
        Utils.skip(ins, 5)
        nb_children = Utils.read_uint8(ins)
        for i in range(nb_children):
            child_prop_id_1 = Utils.read_uint32(ins)
            child_prop_id_2 = Utils.read_uint32(ins)
            assert child_prop_id_1 == child_prop_id_2
            child_prop = registry.get_property_def(child_prop_id_1)
            prop_def.set_child_prop(child_prop)
        nb_unkn_property_ids = Utils.read_uint32(ins)
        for j in range(nb_unkn_property_ids):
            child_prop_id = Utils.read_uint32(ins)
            if not prop_def.has_child_prop(child_prop_id): print('No child prop!')
        num_last = Utils.read_uint32(ins)
        assert num_last == 0

    @staticmethod
    def decode_master_property(buffer: bytearray):
        ins = io.BytesIO(buffer) # Read the whole reader as bytes for IO
        did = Utils.read_uint32(ins)
        Utils.skip(ins, 8)
        assert did == 872415232
        num_strings = Utils.read_tsize(ins)
        registry = PropertiesRegistry()
        for i in range(num_strings):
            pid = Utils.read_uint32(ins)
            name = Utils.read_pascal_string(ins)
            prop_def = PropertyDef(pid, name, None)
            registry.register(prop_def)
        Utils.skip(ins, 2)
        nb_property_defs = Utils.read_tsize(ins)
        for j in range(nb_property_defs):
            pid = Utils.read_uint32(ins)
            PropertyDefinitionsLoader.read_property_def(ins, pid, registry)
        return registry
