import dotenv
import operator
from typing import Annotated, List, Tuple, TypedDict

from IPython.core.display import Image
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Union
from typing import Literal
from langgraph.graph import END
from langgraph.graph import StateGraph, START

dotenv.load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults

async def execute():
    tools = [TavilySearchResults(max_results=3)]

    prompt = 'você é um assistente solicito'

    llm = ChatOpenAI(model_name='gpt-4o-mini')
    agent_executor = create_react_agent(llm, tools, state_modifier=prompt)

    # response = agent_executor.invoke({'messages':'qual a previsão do tempo para belo horizonte?'})
    # print(response)

    class PlanExecute(TypedDict):
        input_message : str
        plan : List[str]
        past_steps : Annotated[List[Tuple], operator.add]
        response : str

    class Plan(BaseModel):
        steps: List[str] = Field(
            description='diferentes passos para seguir, deve ser em ordem'
        )
    planner_prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            """Para o objetivo dado, crie um plano simples passo a passo. 
            Este plano deve envolver tarefas individuais que, se executadas corretamente, produzirão a resposta correta. 
            Não adicione nenhuma etapa supérflua. 
            O resultado da etapa final deve ser a resposta final. 
            Certifique-se de que cada etapa tenha todas as informações necessárias - não pule etapas
            """
        )
    ])

    planner = planner_prompt | ChatOpenAI(model_name='gpt-4o-mini', temperature=0).with_structured_output(Plan)

    # result = planner.invoke({"messages": [("user", "qual a previsão do tempo para belo horizonte?")]})
    # print(result)

    class Response(BaseModel):
        response: str

    class Act(BaseModel):
        action: Union[Response, Plan] = Field(
            description="""Ação a ser executada. Se você quiser responder ao usuário, use Response.
                        Se você precisar usar mais ferramentas para obter a resposta, use Plan."""
        )
    replanner_prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            """Para o objetivo dado, crie um plano simples passo a passo. 
            Este plano deve envolver tarefas individuais que, se executadas corretamente, produzirão a resposta correta. 
            Não adicione nenhuma etapa supérflua. 
            O resultado da etapa final deve ser a resposta final. 
            Certifique-se de que cada etapa tenha todas as informações necessárias - não pule etapas
            
            seu objetivo era esse:
            {input_message}
            
            seu plano original era esse:
            {plan}
            
            e seus passos anteriores foram esses:
            {past_steps}
            
            Atualize seu plano de acordo. Se não forem necessárias mais etapas e você puder retornar ao usuário, responda com isso. 
            Caso contrário, preencha o plano. Adicione apenas etapas ao plano que ainda **PRECISAM** ser feitas. 
            Não retorne etapas feitas anteriormente como parte do plano
            """
        )
    ])

    replanner = replanner_prompt | ChatOpenAI(model_name='gpt-4o-mini', temperature=0).with_structured_output(Act)

    async def execute_step(state: PlanExecute):
        plan = state['plan']
        plan_str = '\n'.join(f"{i + 1}.{step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""para o dado plano:
        {plan_str}\n\nVocê está encarregado de executar a etapa {1}, {task}."""
        agent_response = await agent_executor.ainvoke(
            {
                "messages": [("user", task_formatted)]
            }
        )

        return {
            "past_steps": [(task, agent_response['messages'][-1].content)],
        }

    async def plan_step(state: PlanExecute):
        plan = await planner.ainvoke({"messages": [("user", state['input_message'])]})
        return {
            "plan": plan.steps
        }

    async def replan_step(state: PlanExecute):
        output = await replanner.ainvoke(state)
        if isinstance(output.action, Response):
            return {
                "response": output.action.response
            }
        else:
            return {
                "plan": output.action.steps
            }

    def should_end(state: PlanExecute):
        if "response" in state and state["response"]:
            return END
        else:
            return "agent"

    workflow = StateGraph(PlanExecute)
    workflow.add_node("planner", plan_step)
    workflow.add_node("agent", execute_step)
    workflow.add_node("replan", replan_step)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")
    workflow.add_edge("agent", "replan")
    workflow.add_conditional_edges(
        "replan",
        should_end,
        ["agent", END],
    )
    app = workflow.compile()
    img = Image(app.get_graph(xray=True).draw_mermaid_png())
    with open('plan_and_execute.png', 'wb') as f:
        f.write(img.data)

    config = {"recursion_limit": 50}
    inputs = {"input_message": "qual a previsão do tempo para Belo Horizonte para amanhã?"}
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)

if __name__ =='__main__':
    import asyncio
    asyncio.run(execute())