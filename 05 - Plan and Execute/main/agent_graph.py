from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph

from entities.prompts import EXECUTOR_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT
from main.base_agent import AgentConfig, Agent, Act
from main.plans import PlanExecute, Plan


class  AgentGraph(StateGraph):
    def __init__(self):
        super().__init__(PlanExecute)
        executor_tools = [TavilySearchResults(max_results=3)]
        executor_config = AgentConfig(agent_name='executor',
                                      tools=executor_tools)
        self.agent_executor = Agent(agent_config=executor_config,
                                    agent_prompt=EXECUTOR_PROMPT).create_agent()
        planner_config = AgentConfig(agent_name='planner',
                                     structured_output=Plan)
        self.agent_planner = Agent(agent_config=planner_config,
                                   agent_prompt=PLANNER_PROMPT).create_agent()
        replanner_config = AgentConfig(agent_name='replanner',
                                       structured_output=Act)
        self.agent_replanner = Agent(agent_config=replanner_config,
                                     agent_prompt=REPLANNER_PROMPT).create_agent()
