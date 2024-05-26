from enum import Enum


class Role(Enum):
    ADMIN = 'ADMIN'
    USER ='USER'

    @classmethod
    def choices(cls):
     return [(key.value, key.name) for key in cls]
