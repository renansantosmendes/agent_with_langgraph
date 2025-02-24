from typing import (
    Annotated,
    Sequence,
    TypedDict, Literal
)
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import json
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()


def main():
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]


    model = ChatOpenAI(model="gpt-4o-mini")

    @tool
    def get_weather(location: str):
        """
            Retrieves the current weather data for a given location.

            Args:
                location (str): The city or location for which to retrieve the weather data.

            Returns:
                dict: A dictionary containing the current weather data, including temperature, humidity, wind speed, and more.

            Raises:
                ValueError: If the location is not found or the weather data cannot be retrieved.

            Example:
                >>> get_weather("New York")
                {'temperature': 22, 'humidity': 60, 'wind_speed': 10, ...}
            """
        # This is a placeholder for the actual implementation
        # Don't let the LLM know this though
        if any([city in location.lower() for city in ["sf", "san francisco"]]):
            return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."
        else:
            return f"I am not sure what the weather is in {location}"

    tools = [get_weather]
    model = model.bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    def tool_node(state: AgentState) -> Command[Literal['call_model', 'should_continue']]:
        outputs = []
        for tool_call in state['messages'][-1].tool_calls:
            tool_result = tools_by_name[tool_call['name']].invoke(tool_call['args'])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call['name'],
                    tool_call_id=tool_call['id'],
                )
            )
        goto = 'call_model'
        return Command(goto=goto,
                       update={'messages': outputs})

    def call_model(
            state: AgentState,
            config: RunnableConfig
    ) -> Command[Literal['should_continue']]:
        system_prompt = SystemMessage(
            """Você é um assistente de IA. Responda às dúvidas dos 
            usuários da melhor forma possível!"""
        )
        response = model.invoke([system_prompt] + state['messages'], config)
        return Command(goto='should_continue',
                       update={'messages': [response]})

    def should_continue(state: AgentState) -> Command[Literal['call_model', 'tool_node', '__end__']]:
        messages = state['messages']
        last_message = messages[-1]

        if isinstance(last_message, HumanMessage):
            goto = 'call_model'
        elif not last_message.tool_calls:
            goto = END
        else:
            goto = 'tool_node'
        return Command(goto=goto,
                       update={'messages': messages})

    workflow = StateGraph(AgentState)

    workflow.add_node("call_model", call_model)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("should_continue", should_continue)
    workflow.set_entry_point("should_continue")
    graph = workflow.compile()

    def print_stream(stream):
        for s in stream:
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

    inputs = {"messages": [("user", "como está o tempo em san francisco?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))


if __name__ == "__main__":
    main()
