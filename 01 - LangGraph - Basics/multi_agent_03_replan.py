from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


def main():
    tools = [TavilySearchResults(max_results=3)]

    prompt = hub.pull("ih/ih-react-agent-executor")
    prompt.pretty_print()

    llm = ChatOpenAI(model="gpt-4-turbo-preview")
    agent_executor = create_react_agent(llm, tools, state_modifier=prompt)
    response = agent_executor.invoke({"messages": [("user", "who is the winnner of the us open")]})
    print(response)

    class PlanExecute(TypedDict):
        input: str
        plan: List[str]
        past_steps: Annotated[List[Tuple], operator.add]
        response: str

    class Plan(BaseModel):
        """Plan to follow in future"""

        steps: List[str] = Field(
            description="different steps to follow, should be in sorted order"
        )

    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
            ),
            ("placeholder", "{messages}"),
        ]
    )
    planner = planner_prompt | ChatOpenAI(
        model="gpt-4o", temperature=0
    ).with_structured_output(Plan)

    response = planner.invoke(
        {
            "messages": [
                ("user", "what is the hometown of the current Australia open winner?")
            ]
        }
    )

    print(response)


if __name__ == '__main__':
    main()
