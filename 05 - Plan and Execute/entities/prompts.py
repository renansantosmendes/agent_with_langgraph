EXECUTOR_PROMPT = """Você é um assistente solicito"""

PLANNER_PROMPT = """Para o objetivo dado, crie um plano simples passo a passo. 
            Este plano deve envolver tarefas individuais que, se executadas corretamente, produzirão a resposta correta. 
            Não adicione nenhuma etapa supérflua. 
            O resultado da etapa final deve ser a resposta final. 
            Certifique-se de que cada etapa tenha todas as informações necessárias - não pule etapas
            """

REPLANNER_PROMPT = """Para o objetivo dado, crie um plano simples passo a passo. 
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