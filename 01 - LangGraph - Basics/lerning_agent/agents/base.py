from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable


class BaseAgent(ABC):
    """
    Abstract base class for agents that interact with a chat model.

    Attributes:
        prompt (ChatPromptTemplate): The prompt template used for the chat model.
        llm_model (BaseChatModel): The language model used for the chat.
        llm_model_with_tools (Runnable, optional): The language model bound to tools. Defaults to None.
        agent_name (str): The name of the agent.
        tools (list, optional): The list of tools available to the agent. Defaults to None.

    Methods:
        __init__(): Initializes the agent and sets up the language model with tools if available.
        _initialize_model_with_tools(): Binds the language model to tools if tools are available.
        call_llm(): Abstract method to call the language model. Must be implemented by subclasses.
    """
    prompt: ChatPromptTemplate
    llm_model: BaseChatModel
    llm_model_with_tools: Runnable = None
    agent_name: str
    tools: Optional[list] = None

    def __init__(self, **kwargs):
        """
        Initializes the agent and sets up the language model with tools if available.

        Args:
            prompt (ChatPromptTemplate): The prompt template used for the chat model.
            llm_model (BaseChatModel): The language model used for the chat.
            llm_model_with_tools (Runnable, optional): The language model bound to tools. Defaults to None.
            agent_name (str, optional): The name of the agent. Defaults to "".
            tools (list, optional): The list of tools available to the agent. Defaults to None.

        Returns:
            None
        """
        self._initialize_model_with_tools()

    def _initialize_model_with_tools(self):
        """
        Binds the language model to tools if tools are available.

        This method is called during initialization and sets up the language model with tools if provided.

        Returns:
            None
        """
        if self.tools:
            self.llm_model_with_tools = self.llm_model.bind_tools(self.tools)

    @abstractmethod
    def call_llm(self, **kwargs) -> BaseMessage:
        ...
