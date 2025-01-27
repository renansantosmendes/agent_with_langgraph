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


class AgentGraph(StateGraph):
    """
    A state graph representing the planning and execution of tasks by agents.

    This class orchestrates a workflow involving a planner, an executor, and a replanner
    to process and execute tasks based on input messages and plans.

    Attributes:
        executor (Agent): The agent responsible for executing individual steps of the plan.
        planner (Agent): The agent responsible for creating a plan from an input message.
        replanner (Agent): The agent responsible for replanning if adjustments are needed.
        _workflow_compiled (Optional[Callable]): The compiled workflow for execution.
    """

    def __init__(self):
        """
        Initializes the `AgentGraph` with pre-configured planner, executor, and replanner agents.
        """
        super().__init__(PlanExecute)
        executor_tools = [TavilySearchResults(max_results=3)]
        executor_config = AgentConfig(agent_name='executor',
                                      tools=executor_tools)
        self.executor = Agent(config=executor_config,
                              agent_prompt=EXECUTOR_PROMPT).create_custom_react_agent()
        planner_config = AgentConfig(agent_name='planner',
                                     structured_output=Plan)
        self.planner = Agent(config=planner_config,
                             agent_prompt=PLANNER_PROMPT).create_agent()
        replanner_config = AgentConfig(agent_name='replanner',
                                       structured_output=Act)
        self.replanner = Agent(config=replanner_config,
                               agent_prompt=REPLANNER_PROMPT).create_agent()
        self._workflow_compiled = None

    def execute(self, state: PlanExecute) -> Command[Literal["replan"]]:
        """
        Executes the first step of the plan.

        Args:
            state (PlanExecute): The current state containing the plan and execution details.

        Returns:
            Command[Literal["replan"]]: A command updating the past steps and transitioning to replanning.
        """
        plan = state['plan']
        plan_str = '\n'.join(f"{i + 1}.{step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""For the given plan:
        {plan_str}\n\nYou are responsible for executing step {1}, {task}."""
        agent_response = self.executor.invoke(
            {
                "messages": [("user", task_formatted)]
            }
        )
        return Command(update={
            "past_steps": [(task, agent_response['messages'][-1].content)],
        }, goto="replan")

    def plan(self, state: PlanExecute) -> Command[Literal["agent"]]:
        """
        Generates a plan based on the input message.

        Args:
            state (PlanExecute): The current state containing the input message.

        Returns:
            Command[Literal["agent"]]: A command updating the state with the plan and transitioning to execution.
        """
        plan = self.planner.invoke({"messages": [("user", state['input_message'])]})
        return Command(update={
            "plan": plan.steps
        }, goto="agent")

    def replan(self, state: PlanExecute) -> Command[Literal["agent", "END"]]:
        """
        Handles replanning or generates a final response.

        Args:
            state (PlanExecute): The current state containing the execution history and plan.

        Returns:
            Command[Literal["agent", "END"]]: A command updating the state with a new plan or final response,
            and transitioning to execution or ending the process.
        """
        output = self.replanner.invoke(state)
        if isinstance(output.action, Response):
            return Command(update={
                "response": output.action.response
            }, goto=END)
        else:
            return Command(update={
                "plan": output.action.steps
            }, goto="agent")

    def _build_workflow(self) -> None:
        """
        Builds the workflow for the state graph.

        Adds nodes and transitions for planner, executor, and replanner states, then compiles the workflow.
        """
        workflow = StateGraph(PlanExecute)
        workflow.add_node("planner", self.plan)
        workflow.add_node("agent", self.execute)
        workflow.add_node("replan", self.replan)
        workflow.set_entry_point("planner")
        self._workflow_compiled = workflow.compile()

    def build(self):
        """
        Builds and returns the compiled workflow.

        Returns:
            Callable: The compiled workflow for execution.
        """
        self._build_workflow()
        return self._workflow_compiled

    def save_image(self) -> None:
        """
        Saves a visual representation of the workflow as a PNG image.

        The workflow graph is rendered using Mermaid and saved to a file named 'plan_and_execute.png'.
        """
        img = Image(
            self._workflow_compiled.get_graph(xray=True).draw_mermaid_png()
        )
        with open('plan_and_execute.png', 'wb') as f:
            f.write(img.data)

