from typing import Union, Optional, Any, Sequence

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from plans import Plan


class Response(BaseModel):
    response: str


class Act(BaseModel):
    action: Union[Response, Plan] = Field(
        description="""Ação a ser executada. Se você quiser responder ao usuário, use Response.
                    Se você precisar usar mais ferramentas para obter a resposta, use Plan."""
    )


class AgentConfig(BaseModel):
    agent_name: str = Field(description='The agent name')
    model_name: str = Field(description='The model name', default='gpt-4o')
    tools: Optional[Sequence[BaseTool]] = Field(description='The tools to use')
    temperature: float = Field(description='The temperature to use', default=0.0)
    structured_output: Optional[Any] = Field(description='The structured output to use', default=None)


class Agent(BaseModel):
    def __init__(self, agent_config: AgentConfig, agent_prompt: str) -> None:
        super().__init__()
        self.config = agent_config
        self.agent_prompt = agent_prompt

    def _get_llm(self):
        if self.config.structured_output:
            return self._configured_llm().with_structured_output(self.config.structured_output)
        return self._configured_llm()

    def _configured_llm(self):
        return ChatOpenAI(model_name=self.config.model_name,
                          temperature=self.config.temperature)

    def create_agent(self):
        return ChatPromptTemplate.from_template(self.agent_prompt) | create_react_agent(
            llm=self._get_llm(),
            tools=self.config.tools,
            state_modifier=self.agent_prompt
        )


