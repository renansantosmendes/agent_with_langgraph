from datetime import datetime

from pydantic import BaseModel, PydanticUserError, ValidationError, RootModel, ConfigDict, validate_call


def main():
    # class User(BaseModel):
    #     id: int
    #     name: str = "Jane Doe"
    #     signup_ts: datetime | None = None
    #
    # user = User(id='123')
    # print(user)
    # print(user.model_dump())
    #
    # print('-'*10, 'rebuild', '-'*10)
    #
    # class Foo(BaseModel):
    #     x: 'Bar'
    #
    # try:
    #     Foo.model_json_schema()
    # except PydanticUserError as e:
    #     print(e)
    #
    # class Bar(BaseModel):
    #     pass
    #
    # Foo.model_rebuild()
    # print(Foo.model_json_schema())
    #
    # print('-' * 10, 'model_validation', '-' * 10)
    # print(User.model_validate({'id': 123, 'name': 'James'}))
    #
    # try:
    #     User.model_validate(['test'])
    # except ValidationError as e:
    #     print(e)
    #
    #
    # print( User.model_validate_json('{"id": 123, "name": "James"}'))
    #
    # try:
    #     m = User.model_validate_json('{"id": 123, "name": 123}')
    # except ValidationError as e:
    #     print(e)
    #
    # print('-' * 10, 'root_model', '-' * 10)
    # Pets = RootModel[list[str]]
    # print(Pets.model_json_schema())

    print('-' * 10, 'strict_mode', '-' * 10)

    class User2(BaseModel):
        model_config = ConfigDict(strict=True)
        name: str
        age: int
        is_active: bool

    try:
        User2.model_validate({'name': 'John', 'age': '30', 'is_active': True})
    except ValidationError as e:
        print(e)

    @validate_call(config=ConfigDict(strict=True))
    def foo(x: int, y: int) -> int:
        return x + y

    try:
        print(foo('1', '2'))
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
