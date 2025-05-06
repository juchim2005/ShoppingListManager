class Product:
    def __init__(self, name, price, category,is_18_plus):
        self.name = name
        self.price = price
        self.category = category
        self.is_18_plus = is_18_plus

    def __str__(self):
        return f"{self.name}"