def main():
    import time

    class CustomerDirect:
        def __init__(self):
            self.discount = 0.10

    class CustomerProperty:
        @property
        def discount(self):
            return 0.10

    # Teste de velocidade
    direct = CustomerDirect()
    prop = CustomerProperty()

    # Tempo de acesso ao atributo direto
    start = time.perf_counter()
    for _ in range(100_000_000):
        d = direct.discount
    end = time.perf_counter()
    print(f"Acesso direto: {end - start:.6f} segundos")

    # Tempo de acesso à @property
    start = time.perf_counter()
    for _ in range(100_000_000):
        d = prop.discount
    end = time.perf_counter()
    print(f"Acesso via @property: {end - start:.6f} segundos")

if __name__ == "__main__":
    main()