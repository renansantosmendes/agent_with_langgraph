from utils import graph

if __name__ == '__main__':
    while True:
        user_input = input("Usuário: ")
        if user_input.lower() in ['sair', 'exit', 's']:
            print('Até logo!')
            break

        for event in graph.stream({'messages': ('user', user_input)}):
            for value in event.values():
                print("AI:", value['messages'][-1].content)
