from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from dotenv import load_dotenv
from typing import Literal
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

load_dotenv()


def main():
    tavily_tool = TavilySearchResults(max_results=5)

    # This executes code locally, which can be unsafe
    repl = PythonREPL()

    @tool
    def python_repl_tool(
        code: Annotated[str, "The python code to execute to generate your chart."],
    ):
        """Use this to execute python code and do math. If you want to see the output of a value,
        you should print it out with `print(...)`. This is visible to the user."""
        try:
            result = repl.run(code)
        except BaseException as e:
            return f"Failed to execute. Error: {repr(e)}"
        result_str = f"Successfully executed:\n\`\`\`python\n{code}\n\`\`\`\nStdout: {result}"
        return result_str

    members = ["researcher", "coder"]
    # Our team supervisor is an LLM node. It just picks the next agent to process
    # and decides when the work is completed
    options = members + ["FINISH"]

    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: Literal[*options]

    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")

    def supervisor_node(state: MessagesState) -> Command[Literal[*members, "__end__"]]:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto)

    research_agent = create_react_agent(
        llm, tools=[tavily_tool], state_modifier="You are a researcher. DO NOT do any math."
    )

    def research_node(state: MessagesState) -> Command[Literal["supervisor"]]:
        result = research_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="researcher")
                ]
            },
            goto="supervisor",
        )

    # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
    code_agent = create_react_agent(llm, tools=[python_repl_tool])

    def code_node(state: MessagesState) -> Command[Literal["supervisor"]]:
        result = code_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="coder")
                ]
            },
            goto="supervisor",
        )

    builder = StateGraph(MessagesState)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)
    graph = builder.compile()
    # for s in graph.stream(
    #         {"messages": [("user", "What's the square root of 42?")]}, subgraphs=True
    # ):
    #     print(s)
    #     print("----")

    for s in graph.stream(
            {
                "messages": [
                    (
                            "user",
                            "Find the latest GDP of New York and California, then calculate the average",
                    )
                ]
            },
            subgraphs=True,
    ):
        print(s)
        print("----")


if __name__ == "__main__":
    main()