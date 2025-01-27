from agents.base_agent import AgentConfig, Agent
from entities.plans import Plan
from entities.prompts import PLANNER_PROMPT
import dotenv


dotenv.load_dotenv()

if __name__ == '__main__':
    planner_config = AgentConfig(agent_name='planner',
                                 structured_output=Plan)
    planner = Agent(config=planner_config,
                    agent_prompt=PLANNER_PROMPT).create_agent()

    plan = planner.invoke({"messages": [("user", 'qual a previsão do tempo para belo horizonte amanha?')]})
    print(plan)