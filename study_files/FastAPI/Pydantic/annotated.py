from typing import Annotated

from pydantic import Field, BaseModel


def main():

    class Person(BaseModel):
        name: str
        age: Annotated[int, Field(gt=0, lt=120)]

if __name__ == "__main__":
    main()