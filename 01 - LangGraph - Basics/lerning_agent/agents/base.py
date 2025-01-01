from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate


class BaseAgent(ABC):
    prompt: ChatPromptTemplate
    llm_model: BaseChatModel
    agent_name: str
    tools: Optional[list] = None

    @abstractmethod
    def call_llm(self) -> BaseMessage:
        ...
