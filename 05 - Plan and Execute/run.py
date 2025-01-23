import dotenv
import operator
from typing import Annotated, List, Tuple, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Union

dotenv.load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults

def execute():
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

if __name__ =='__main__':
    execute()