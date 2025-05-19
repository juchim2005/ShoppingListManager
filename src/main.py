from shoppingList import *
from product import *
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
shoppinglist = ShoppingList()
product = Product("milk",1.99,"dairy",False)
product2 = Product("eggs",0.99,"dairy",False)
shoppinglist.add_product(product,2)
shoppinglist.add_product(product2,3)
product.price = 2.99
shoppinglist.edit_product(product,3,True)
print(shoppinglist.products)
shoppinglist.delete_product(product)
print(shoppinglist.products)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    bought = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"{self.name} - {self.price}"
@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)