import json
import os

from IPython.core.display import Image
from dotenv import load_dotenv

from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

os.environ['LANGCHAIN_PROJECT'] = 'langgraph-study'
load_dotenv()


def main():
    graph_builder = StateGraph(State)

    tool = TavilySearchResults(max_results=2)
    tools = [tool]
    tool_node = ToolNode(tools=[tool])
    memory = MemorySaver()
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {"tools": "tools", END: END},
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("chatbot", END)

    graph = graph_builder.compile(checkpointer=memory)

    img = Image(graph.get_graph().draw_mermaid_png())
    with open('minha_imagem_salva.png', 'wb') as f:
        f.write(img.data)
    config = {"configurable": {"thread_id": "1"}}

    def stream_graph_updates(user_input: str):
        config = {"configurable": {"thread_id": "1"}}
        input_message = {"type": "user", "content": user_input}
        for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
            chunk["messages"][-1].pretty_print()

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except:
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break

if __name__ == '__main__':
    main()
