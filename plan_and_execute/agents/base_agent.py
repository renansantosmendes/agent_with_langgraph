from typing import Optional, Any, Sequence

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    agent_name: str = Field(description='The agent name')
    model_name: str = Field(description='The model name', default='gpt-4o')
    tools: Optional[Sequence[BaseTool]] = Field(description='The tools to use', default=None)
    temperature: float = Field(description='The temperature to use', default=0.0)
    structured_output: Optional[Any] = Field(description='The structured output to use', default=None)


class Agent(BaseModel):
    config: AgentConfig
    agent_prompt: str

    def _get_llm(self):
        if self.config.structured_output:
            return self._configured_llm().with_structured_output(self.config.structured_output)
        return self._configured_llm()

    def _configured_llm(self):
        return ChatOpenAI(model_name=self.config.model_name,
                          temperature=self.config.temperature)

    def create_agent(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.agent_prompt),
                ("placeholder", "{messages}")
        ]) | self._get_llm()

    def create_custom_react_agent(self):
        return ChatPromptTemplate.from_messages(self.agent_prompt) | create_react_agent(
            model=self._get_llm(),
            tools=self.config.tools if self.config.tools else [],
            state_modifier=self.agent_prompt
        )
