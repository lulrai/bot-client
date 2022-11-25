from __future__ import annotations

import json
import os

from backend.paths import DATA_PATH
from backend.utils.common_utils import Utils


class KnownVariablesManager(object):
    _instance = None

    def __new__(cls) -> KnownVariablesManager:
        if not hasattr(cls, 'instance'):
            cls._instance = super(KnownVariablesManager, cls).__new__(cls)
            cls.__cache: dict[int, str] = {}
            cls.__initialize()
        return cls._instance

    @classmethod
    def __load(cls) -> None:
        # Load the known variables from the file in the data folder
        with open(os.path.join(DATA_PATH, 'KnownVariables.json')) as inf:
            known_variables: list[str] = json.load(inf)
        for known_variable in known_variables:
            var_hash = Utils.hash(known_variable)
            cls.__cache[var_hash] = known_variable

    @classmethod
    def __initialize(cls) -> None:
        cls.__cache[65808821] = 'PLAYER'
        cls.__cache[246996147] = 'CLASS'
        cls.__cache[65824981] = 'RACE'
        cls.__cache[788899] = 'CURRENT'
        cls.__cache[104736179] = 'MAX'
        cls.__load()

    @classmethod
    def get_variable_from_hash(cls, var_hash: int) -> str:
        if var_hash in cls.__cache:
            return cls.__cache[var_hash]
        return None
