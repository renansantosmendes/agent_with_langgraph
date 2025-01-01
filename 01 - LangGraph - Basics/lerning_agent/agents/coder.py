from typing import Annotated

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_openai import ChatOpenAI

from base import BaseAgent

from dotenv import load_dotenv

load_dotenv()


@tool
def python_repl_tool(
        code: Annotated[str, "The python code to execute."]
) -> str:
    """Use this to execute Python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        PythonREPL().run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return "Successfully executed"


class CoderAgent(BaseAgent):

    prompt = ChatPromptTemplate.from_messages([
        ('system', 'Você é um programador, que cria e executa códigos em Python.'),
        MessagesPlaceholder(variable_name='code')
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm_model = kwargs.get('llm_model', ChatOpenAI(model="gpt-4o-mini"))
        self.tools = [python_repl_tool]
        self._initialize_model_with_tools()

    def call_llm(self, **kwargs) -> BaseMessage:
        chain = self.prompt | self.llm_model_with_tools
        return chain.invoke(kwargs)


if __name__ == "__main__":
    coder = CoderAgent(llm_model=ChatOpenAI(model="gpt-4o-mini"),
                       agent_name="coder")
    result = coder.call_llm(code=[HumanMessage(content="print('Hello, World!')")])
    print(result)