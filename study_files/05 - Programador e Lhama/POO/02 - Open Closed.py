class Customer:
    def __init__(self, discount: float=0.0) -> None:
        self.discount = discount

class RegularCustomer(Customer):
    def __init__(self) -> None:
        super().__init__(discount=0.05)

class VipCustomer(Customer):
    def __init__(self) -> None:
        super().__init__(discount=0.10)

class PremiumCustomer(Customer):
    def __init__(self) -> None:
        super().__init__(discount=0.15)

class DiscountCalculator:
    @staticmethod
    def calculate_discount(customer: Customer,
                           amount: float)-> float:
        return customer.discount * amount

vip_customer = VipCustomer()
print(DiscountCalculator.calculate_discount(vip_customer, 100))
