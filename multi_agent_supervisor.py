
from dotenv import load_dotenv
from typing import Annotated
from typing import Literal
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, add_messages
from langgraph.types import Command
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def multi_agent_run():
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

    system_prompt = f"""
    Você é um supervisor encarregado de gerenciar uma conversa entre os seguintes
    trabalhadores: {members}. Dada a seguinte solicitação do
    usuário, responda com o trabalhador para agir em seguida. Cada trabalhador
    executará uma tarefa e responderá com seus resultados e status. Quando
    terminar, responda com FINISH.
    """

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next_node: Literal["researcher", "coder", "FINISH"]

    llm = ChatOpenAI(model='gpt-4o-mini')

    def supervisor_node(state: MessagesState) -> Command[Literal["researcher",
                                                                 "coder",
                                                                 "__end__"]]:
        messages = [
          {
              "role": "system", "content": system_prompt
          }
        ] + state['messages']
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response['next_node']
        if goto == 'FINISH':
            goto = END
        return Command(goto=goto)

    research_agent = create_react_agent(
        llm, tools=[tavily_tool],
        state_modifier="Você é um pesquisador, não execute nenhum cálculo matemático."
    )

    code_agent = create_react_agent(llm, tools=[python_repl_tool],
                                    state_modifier="Você é um programador, que cria e executa códigos em Python.")

    def research_node(state: MessagesState) -> Command[Literal["supervisor"]]:
        result = research_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    AIMessage(content=result["messages"][-1].content,
                              name="researcher")
                ]
            },
            goto="supervisor",
        )

    def code_node(state: MessagesState) -> Command[Literal["supervisor"]]:
        result = code_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    AIMessage(content=result["messages"][-1].content,
                              name="coder")
                ]
            },
            goto="supervisor",
        )

    workflow = StateGraph(AgentState)
    workflow.add_edge(START, "supervisor")
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("coder", code_node)
    multi_agent_graph = workflow.compile()

    for s in multi_agent_graph.stream(
        {"messages": [("user", "qual a raíz quadrada de 42?")]}, subgraphs=True
    ):
        print(s)
        print("-"*40)


if __name__ == "__main__":
    multi_agent_run()
