from pydantic import BaseModel
from pydantic import Field
from uuid import uuid4
from typing import Optional


class Class1(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str = Field(default='Renan')
    attribute_1: Optional[str] = Field(default='')
    age: int
    address: str

    # class Config:
    #     populate_by_name = True


if __name__ == "__main__":
    obj1 = Class1(name="John", age=30, address="123 Main St")
    print(obj1)

    obj2 = Class1(age=35, address="123 Main St")
    print(obj2)