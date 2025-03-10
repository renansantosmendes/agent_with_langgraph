import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import ToolMessage


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class Agent(object):
    def __init__(self, model, tools) -> None:
        """
        Initializes the Agent object with the provided model and tools.

        Parameters:
            model: The model used by the agent.
            tools: The tools available for the agent to use.

        Returns:
            None
        """
        self.system = """Você é um assistente de pesquisa inteligente. Use o motor de busca para procurar informações. 
        Você pode fazer várias buscas (juntas ou em sequência). Só procure informações quando tiver certeza do que quer.
         Se precisar buscar alguma informação antes de fazer uma pergunta de acompanhamento, você está autorizado a fazer isso!
        """
        graph = StateGraph(AgentState)
        graph.add_node("llm", action=self.call_openai)
        graph.add_node("action", action=self.take_action)
        graph.add_conditional_edges(
            source="llm",
            path=self.exists_action,
            path_map={True: "action", False: END}
        )
        graph.add_edge(start_key="action", end_key="llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    @staticmethod
    def exists_action(state: AgentState) -> bool:
        """
        A function that checks if there are tool calls in the latest message of the given state.

        Parameters:
            state: An AgentState object representing the current state of the agent.

        Returns:
            bool: True if there are tool calls, False otherwise.
        """
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState) -> dict:
        """
        A function that calls the OpenAI model to generate a message based on the input state.

        Parameters:
            self: The object instance.
            state: An AgentState object representing the current state of the agent.

        Returns:
            dict: A dictionary containing messages generated by the OpenAI model.
        """
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState) -> dict:
        """
        A function that takes action based on the given state by invoking tools, collecting results,
        and returning a dictionary of results.

        Parameters:
            self: The object instance.
            state: An AgentState object representing the current state of the agent.

        Returns:
            dict: A dictionary of results containing messages from the tools.
        """
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for tool in tool_calls:
            print(f"Calling: {tool}")
            if not tool['name'] in self.tools:
                print("\n ....bad tool name....")
                result = "bad tool name, retry"
            else:
                result = self.tools[tool['name']].invoke(tool['args'])
            results.append(ToolMessage(tool_call_id=tool['id'], name=tool['name'],
                                       content=str(result)))
        print("Back to the model!")
        return {'messages': results}
