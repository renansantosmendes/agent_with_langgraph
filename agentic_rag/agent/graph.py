from langgraph.graph import (
    END,
    StateGraph,
    START
)
from langgraph.prebuilt import ToolNode, tools_condition

from agentic_rag.agent.nodes import (
    agent,
    rewrite,
    generate,
    grade_documents
)
from agentic_rag.agent.state import AgentState
from agentic_rag.tools.retrieval import retriever_tool

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent)
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)
workflow.add_node("rewrite", rewrite)
workflow.add_node(
    "generate", generate
)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "retrieve",
        END: END,
    },
)
workflow.add_conditional_edges(
    "retrieve",
    grade_documents,
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

graph = workflow.compile()