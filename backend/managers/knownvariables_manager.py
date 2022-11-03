from __future__ import annotations

import json
import os

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
        with open(os.path.join('..', 'data', 'KnownVariables.json')) as inf:
            known_variables: list[str] = json.load(inf)
        for known_variable in known_variables:
            hash = Utils.hash(known_variable)
            cls.__cache[hash] = known_variable

    @classmethod
    def __initialize(cls) -> None:
        cls.__cache[65808821] = 'PLAYER'
        cls.__cache[246996147] = 'CLASS'
        cls.__cache[65824981] = 'RACE'
        cls.__cache[788899] = 'CURRENT'
        cls.__cache[104736179] = 'MAX'
        cls.__load()

    @classmethod
    def get_variable_from_hash(cls, hash: int) -> str:
        if hash in cls.__cache:
            return cls.__cache[hash]
        return None
