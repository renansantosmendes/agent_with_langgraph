from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import Tool


class BaseAgent:
    def __init__(self,
                 llm_model: BaseChatModel,
                 agent_name: str):
        self.prompt = None
        self.llm_model = llm_model
        self.agent_name = agent_name
        self.messages_history: list[BaseMessage] = []
        self.tools: list[Tool] = []
        self._initialize()

    def _initialize(self):
        self.llm_model = self.llm_model.bind_tools(self.tools)
        self.chain = self.prompt | self.llm_model

    def call_llm(self) -> BaseMessage:
        return self.chain.invoke(self.messages_history)
