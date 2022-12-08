from typing import TypeVar

import humps
import pydantic


T = TypeVar("T")


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True
        alias_generator = humps.camelize
        allow_population_by_field_name = True
