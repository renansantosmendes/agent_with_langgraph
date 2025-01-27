import operator
from typing import List, Annotated, Tuple

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class PlanExecute(TypedDict):
    """
     Represents the execution details of a plan.

     Attributes:
         input_message (str): The input message that initiated the plan.
         plan (List[str]): A list of steps to be executed as part of the plan.
         past_steps (Annotated[List[Tuple], operator.add]): A history of past steps executed, represented as a list of tuples.
         response (str): The agent's response after executing the plan.
     """
    input_message: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


class Plan(BaseModel):
    """
    Represents a plan with a sequence of steps.

    Attributes:
        steps (List[str]): A list of sequential steps to be followed, provided in order.
    """
    steps: List[str] = Field(
        description='diferentes passos para seguir, deve ser em ordem'
    )