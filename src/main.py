from shoppingList import *
from product import *
shoppinglist = ShoppingList()
product = Product("milk",1.99,"dairy",False)
shoppinglist.add_product(product,2)
print(shoppinglist.products)