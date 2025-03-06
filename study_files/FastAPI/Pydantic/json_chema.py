import json
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


def main():
    class FooBar(BaseModel):
        count: int
        size: float | None = None

    class Gender(str, Enum):
        male = "male"
        female = "female"
        other = "other"
        not_given = 'not_given'

    class MainModel(BaseModel):
        model_config = ConfigDict(title='Main')

        foo_bar: FooBar
        gender: Annotated[Gender | None, Field(alias='gender')]
        snap: int = Field(
            default=42,
            title='The snap',
            description='this is the value of snap',
            gt=30,
            lt=50,
        )

    print(json.dumps(MainModel.model_json_schema(), indent=2))

if __name__ == "__main__":
    main()