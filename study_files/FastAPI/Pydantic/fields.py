from uuid import uuid4

from pydantic import Field, BaseModel


def main():
    class User(BaseModel):
        id : str = Field(default_factory= lambda : uuid4().hex)
        name: str = Field(alias='username')

    user = User(username='John Doe')
    print(user.model_dump())
    print(user.model_dump(by_alias=True))

    class User2(BaseModel):
        id : str = Field(default_factory= lambda : uuid4().hex)
        name: str = Field(validation_alias='username')

    user = User2(username='John Doe')
    print(user.model_dump())
    print(user.model_dump(by_alias=True))

    class User3(BaseModel):
        id: str = Field(default_factory=lambda: uuid4().hex)
        name: str = Field(serialization_alias='username')

    user = User3(name='John Doe')
    print(user.model_dump())
    print(user.model_dump(by_alias=True))


if __name__ == "__main__":
    main()