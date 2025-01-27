from typing import Optional, Any, Sequence

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """
     Configuration for an AI agent.

     Attributes:
         agent_name (str): The name of the agent.
         model_name (str): The name of the language model to use. Defaults to 'gpt-4o'.
         tools (Optional[Sequence[BaseTool]]): A sequence of tools the agent can use. Defaults to None.
         temperature (float): The temperature parameter for controlling the randomness of the model's output. Defaults to 0.0.
         structured_output (Optional[Any]): The structured output format for the agent. Defaults to None.
     """
    agent_name: str = Field(description='The agent name')
    model_name: str = Field(description='The model name', default='gpt-4o')
    tools: Optional[Sequence[BaseTool]] = Field(description='The tools to use', default=None)
    temperature: float = Field(description='The temperature to use', default=0.0)
    structured_output: Optional[Any] = Field(description='The structured output to use', default=None)


class Agent(BaseModel):
    """
       A class representing an AI agent.

       Attributes:
           config (AgentConfig): Configuration settings for the agent.
           agent_prompt (str): The prompt that defines the agent's behavior and context.
       """
    config: AgentConfig
    agent_prompt: str

    def _get_llm(self):
        """
        Returns a configured language model (LLM).

        If a structured output is specified in the configuration, the LLM will be
        set up to produce structured output. Otherwise, a default configuration is used.

        Returns:
            ChatOpenAI: The configured language model instance.
        """
        if self.config.structured_output:
            return self._configured_llm().with_structured_output(self.config.structured_output)
        return self._configured_llm()

    def _configured_llm(self):
        """
        Configures the language model (LLM) based on the agent's configuration.

        The model is configured with the specified model name and temperature.

        Returns:
            ChatOpenAI: The configured language model instance.
        """
        return ChatOpenAI(model_name=self.config.model_name,
                          temperature=self.config.temperature)

    def create_agent(self):
        """
         Creates an agent using a ChatPromptTemplate.

         This method uses the agent's prompt and configuration to set up a
         prompt template for the agent and link it with the configured language model.

         Returns:
             RunnableSequence: A pipeline combining the prompt template and the language model.
         """
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.agent_prompt),
                ("placeholder", "{messages}")
        ]) | self._get_llm()

    def create_custom_react_agent(self):
        """
        Creates a custom reactive agent.

        This agent is set up with tools (if specified) and a state modifier based on
        the agent's prompt. It uses the configured language model.

        Returns:
            ReactAgent: A reactive agent instance.
        """
        return create_react_agent(
            model=self._get_llm(),
            tools=self.config.tools if self.config.tools else [],
            state_modifier=self.agent_prompt
        )
