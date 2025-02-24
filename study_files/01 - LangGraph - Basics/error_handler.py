from typing import Any
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    Runnable,
    RunnableConfig
)

# Criando um Runnable que passa a entrada sem modificá-la
runnable = RunnablePassthrough()

# Combinando com outro Runnable que modifica a entrada
runnable_parallel = RunnableParallel(origin=runnable, modified=lambda x: x + 1)

# Invocando o Runnable
resultado = runnable_parallel.invoke(1)
print(resultado)
