import random
from typing import TypedDict, Annotated, Literal

from langgraph.constants import START
from langgraph.graph import add_messages
from langgraph.graph import StateGraph
from langgraph.types import Command
from IPython.display import Image


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]

def node_a(state: GraphState) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["a", "b"])
    if value == "a":
        goto = "node_b"
    else:
        goto = "node_c"

    return Command(
        update={"messages": value},
        goto=goto,
    )


def node_b(state: GraphState):
    print("Called B")
    return {"messages": state["messages"] + ["b"]}


def node_c(state: GraphState):
    print("Called C")
    return {"messages": state["messages"] + ["c"]}

def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_edge(START, "node_a")
    workflow.add_node(node_a)
    workflow.add_node(node_b)
    workflow.add_node(node_c)

    compiled_graph = workflow.compile()



    img =Image(compiled_graph.get_graph().draw_mermaid_png())
    with open('minha_imagem_salva.png', 'wb') as f:
        f.write(img.data)
    return compiled_graph

if __name__ == "__main__":
    graph = build_graph()
    response = graph.invoke({"messages": []})

    print(response)