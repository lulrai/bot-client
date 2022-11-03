import json
import os

class CharUtils():
    @staticmethod
    def get_character_class_from_id(id: int) -> str:
        if id == 214: return 'Beorning'
        if id == 40: return 'Burglar'
        if id == 215: return 'Brawler'
        if id == 24: return 'Captain'
        if id == 172: return 'Champion'
        if id == 23: return 'Guardian'
        if id == 162: return 'Hunter'
        if id == 185: return 'Lore-Master'
        if id == 31: return 'Minstrel'
        if id == 193: return 'Rune-Keeper'
        if id == 194: return 'Warden'
        if id == 71: return 'Reaver'
        if id == 128: return 'Defiler'
        if id == 127: return 'Weaver'
        if id == 179: return 'Blackarrow'
        if id == 52: return 'Warleader'
        if id == 126: return 'Stalker'
        return None

    @staticmethod
    def get_race_from_id(id: int) -> str:
        if id == 23: return 'Man'
        if id == 65: return 'Elf'
        if id == 73: return 'Dwarf'
        if id == 81: return 'Hobbit'
        if id == 114: return 'Beorning'
        if id == 117: return 'High-Elf'
        if id == 120: return 'Stout-Axe Dwarf'
        return None

    @staticmethod
    def get_nationality_from_id(id: int) -> str:
        if id == 17: return 'Bree-land'
        if id == 16: return 'Dale'
        if id == 6: return 'Gondor'
        if id == 5: return 'Rohan'
        if id == 15: return 'Lindon'
        if id == 8: return 'Lorien'
        if id == 11: return 'Mirkwood'
        if id == 7: return 'Rivendell'
        if id == 2: return 'Edhellond'
        if id == 4: return 'Blue Mountains'
        if id == 3: return 'Iron Hills'
        if id == 12: return 'Lonely Mountain'
        if id == 10: return 'Grey Mountains'
        if id == 9: return 'White Mountains'
        if id == 18: return 'Fallohides'
        if id == 14: return 'Harfoot'
        if id == 13: return 'Stoors'
        if id == 19: return 'Vales of Anduin'
        if id == 21: return 'Beleriand'
        if id == 22: return 'Imladris'
        if id == 26: return 'Nargothrond'
        if id == 23: return 'Gondolin'
        if id == 24: return 'Ossiriand'
        if id == 27: return 'Mordor Mountains'
        return None

    @staticmethod
    def get_account_type_from_id(id: int) -> str:
        if id == 1: return 'Free To Play'
        if id == 3: return 'Premium'
        if id == 6: return 'VIP'
        if id == 7: return 'Lifetime' 
        return None

    @staticmethod
    def get_vocation_by_id(id: int) -> str:
        if id == 1879062809: return 'Armourer'
        if id == 1879062810: return 'Explorer'
        if id == 1879062811: return 'Armsman'
        if id == 1879062812: return 'Tinker'
        if id == 1879062813: return 'Yeoman'
        if id == 1879062814: return 'Woodsman'
        if id == 1879062815: return 'Historian'
        return None

    @staticmethod
    def retrieve_currency_amounts(copper: int) -> tuple[int]:
        if copper is None: return 0,0,0
        gold: int = copper // 100000
        silver: int = (copper % 100000) // 100
        copper: int = copper % 100
        return gold, silver, copper

    @staticmethod
    def retrieve_title_by_id(id: int) -> str:
        if id is None: return None
        with open(os.path.join('..', 'data', 'titles.json')) as title_file:
            titles = json.load(title_file)
            return titles[str(id)]['name']

    @staticmethod
    def retrieve_location_by_id(id: int) -> str:
        if id is None: return None
        with open(os.path.join('..', 'data', 'areas.json')) as areas_file:
            areas = json.load(areas_file)
            area = areas.get('area').get(str(id))
            if area is None: return ''
            territory = areas.get('territory').get(area.get('parentId'))
            if territory is None: return ''
            region = areas.get('region').get(territory.get('parentId'))
            if region is None: return ''
            return area.get('name') + ', ' + territory.get('name') + ', ' + region.get('name')