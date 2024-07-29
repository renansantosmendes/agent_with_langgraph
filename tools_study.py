from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Add2(BaseModel):
    """add two numbers together"""
    a: int = Field(..., description='first number')
    b: int = Field(..., description='second number')


class Multiply2(BaseModel):
    """multiply two numbers together"""
    a: int = Field(..., description='first number')
    b: int = Field(..., description='second number')


def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b


tools = [add, multiply]

if __name__ == '__main__':
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools)

    query = "What is 3 * 12?"

    response = llm_with_tools.invoke(query)
    print(response)
    print(response.additional_kwargs['tool_calls'][0]['function']['arguments'])

    response_2 = llm_with_tools.invoke('o que é machine learning?')
    print(response_2)
