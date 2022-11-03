class PropertyType:
    Undef = 0
    String = 1
    StringToken = 2
    Waveform = 3
    TimeStamp = 4
    TriState = 5
    Vector = 6
    InstanceID = 7
    EnumMapper = 8
    Float = 9
    PropertyID = 10
    Struct = 11
    Array = 12
    StringInfo = 13
    Bitfield64 = 14
    Int = 15
    Color = 16
    Position = 17
    Bitfield32 = 18
    Int64 = 19
    DataFile = 20
    Bool = 21
    Bitfield = 22
    NAMES = {
        0: 'Undef',
        1: 'String',
        2: 'StringToken',
        3: 'Waveform',
        4: 'TimeStamp',
        5: 'TriState',
        6: 'Vector',
        7: 'InstanceID',
        8: 'EnumMapper',
        9: 'Float',
        10: 'PropertyID',
        11: 'Struct',
        12: 'Array',
        13: 'StringInfo',
        14: 'Bitfield64',
        15: 'Int',
        16: 'Color',
        17: 'Position',
        18: 'Bitfield32',
        19: 'Int64',
        20: 'DataFile',
        21: 'Bool',
        22: 'Bitfield'
    }
    INDICES = {v: k for k, v in NAMES.items()}

    def __init__(self, val) -> None:
        assert isinstance(val, int)
        assert 1 <= val <= 22
        self.val = val