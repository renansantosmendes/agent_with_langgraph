from typing import Literal

from IPython.core.display import Image
from langchain_community.tools import TavilySearchResults
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Command

from entities.prompts import EXECUTOR_PROMPT, PLANNER_PROMPT, REPLANNER_PROMPT
from plan_and_execute.agents.base_agent import AgentConfig, Agent
from agents.models import Act, Response
from entities.plans import PlanExecute, Plan


class  AgentGraph(StateGraph):
    def __init__(self):
        super().__init__(PlanExecute)
        executor_tools = [TavilySearchResults(max_results=3)]
        executor_config = AgentConfig(agent_name='executor',
                                      tools=executor_tools)
        self.executor = Agent(config=executor_config,
                              agent_prompt=EXECUTOR_PROMPT).create_agent()
        planner_config = AgentConfig(agent_name='planner',
                                     structured_output=Plan)
        self.planner = Agent(config=planner_config,
                             agent_prompt=PLANNER_PROMPT).create_agent()
        replanner_config = AgentConfig(agent_name='replanner',
                                       structured_output=Act)
        self.replanner = Agent(config=replanner_config,
                               agent_prompt=REPLANNER_PROMPT).create_agent()
        self._workflow_compiled = None

    async def execute(self, state: PlanExecute) -> Command[Literal["replan"]]:
        plan = state['plan']
        plan_str = '\n'.join(f"{i + 1}.{step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""para o dado plano:
        {plan_str}\n\nVocê está encarregado de executar a etapa {1}, {task}."""
        agent_response = await self.executor.ainvoke(
            {
                "messages": [("user", task_formatted)]
            }
        )
        return Command(update={
            "past_steps": [(task, agent_response['messages'][-1].content)],
        }, goto="replan")

    async def plan(self, state: PlanExecute) -> Command[Literal["agent"]]:
        plan = await self.planner.ainvoke({"messages": [("user", state['input_message'])]})
        return Command(update={
            "plan": plan.steps
        }, goto="agent")

    async def replan(self, state: PlanExecute) -> Command[Literal["agent", "END"]]:
        output = await self.replanner.ainvoke(state)
        if isinstance(output.action, Response):
            return Command(update={
                "response": output.action.response
            }, goto=END)
        else:
            return Command(update={
                "plan": output.action.steps
            }, goto="agent")

    def _build_workflow(self) -> None:
        workflow = StateGraph(PlanExecute)
        workflow.add_node("planner", self.plan)
        workflow.add_node("agent", self.execute)
        workflow.add_node("replan", self.replan)
        workflow.set_entry_point("planner")
        self._workflow_compiled = workflow.compile()

    def build(self):
        self._build_workflow()
        return self._workflow_compiled

    def save_image(self) -> None:
        img = Image(
            self._workflow_compiled .get_graph(xray=True).draw_mermaid_png()
        )
        with open('plan_and_execute.png', 'wb') as f:
            f.write(img.data)
