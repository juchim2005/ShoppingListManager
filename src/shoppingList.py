import pandas as pd
class ShoppingList:
    def __init__(self):
        self.products = pd.DataFrame(columns=["product", "amount", "price","bought"])

    def add_product(self, product,amount,bought=False):
        new_product = pd.DataFrame([[product,amount, product.price*amount,bought]], columns=["product", "amount", "price","bought"])
        self.products = pd.concat([self.products, new_product], ignore_index=True)
    
    def edit_product(self, product,amount,bought=False):
        self.products.loc[self.products["product"] == product, ["amount","price","bought"]] = [amount,product.price*amount,bought]

    def delete_product(self, product):
        self.products = self.products[self.products["product"] != product]
        self.products.reset_index(drop=True, inplace=True)