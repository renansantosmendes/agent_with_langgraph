from langchain_core.runnables import RunnableLambda

if __name__ == "__main__":
    runnable = RunnableLambda(lambda x: str(x))
    result_1 = runnable.invoke(5)
    print(type(result_1))
    print(result_1)

    result_2 = runnable.batch([1, 2, 3])
    print(result_2)