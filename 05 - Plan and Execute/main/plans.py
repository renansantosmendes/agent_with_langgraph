import operator
from typing import List, Annotated, Tuple

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class PlanExecute(TypedDict):
    input_message: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


class Plan(BaseModel):
    steps: List[str] = Field(
        description='diferentes passos para seguir, deve ser em ordem'
    )