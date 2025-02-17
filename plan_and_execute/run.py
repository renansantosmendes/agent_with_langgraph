import dotenv

from agents.agent_graph import AgentGraph

dotenv.load_dotenv()


def execute_agent():
    config = {"recursion_limit": 50}
    inputs = {"input_message": "qual a previsão do tempo para Belo Horizonte para amanhã?"}
    agent = AgentGraph().build()
    for event in agent.stream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ =='__main__':
    execute_agent()
