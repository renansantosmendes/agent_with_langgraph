from typing import Union
from pydantic import BaseModel, Field
from entities.plans import Plan


class Response(BaseModel):
    response: str


class Act(BaseModel):
    action: Union[Response, Plan] = Field(
        description="""Ação a ser executada. Se você quiser responder ao usuário, use Response.
                    Se você precisar usar mais ferramentas para obter a resposta, use Plan."""
    )
