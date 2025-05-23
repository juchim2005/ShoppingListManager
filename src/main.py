from enum import Enum
from sqlalchemy import Enum as SqlEnum
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class CategoryEnum(Enum):
    WARZYWA = 'Warzywa'
    OWOCE = 'Owoce'
    NABIAŁ = 'Nabiał'
    PIECZYWO = 'Pieczywo'
    NAPOJE = "Napoje"
    INNE = 'Inne'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(SqlEnum(CategoryEnum), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    bought = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category.value,
            "quantity": self.quantity,
            "bought": self.bought
        }

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/products", methods=["GET", "POST"])
def handle_products():
    if request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        price = data.get("price")
        category = CategoryEnum(data.get("category"))
        quantity = data.get("quantity")
        bought = False

        if not name or not price or not category:
            return jsonify({"error": "Missing product data"}), 400

        new_product = Product(
            name=name.strip(),
            price=float(price),
            category=category,
            quantity=int(quantity),
            bought=bought
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    query = Product.query

    category = request.args.get("category")
    if category:
        try:
            query = query.filter(Product.category == CategoryEnum(category))
        except ValueError:
            return jsonify({"error": f"Invalid category: {category}"}), 400

    bought = request.args.get("bought")
    if bought is not None:
        if bought.lower() == "true":
            query = query.filter(Product.bought.is_(True))
        elif bought.lower() == "false":
            query = query.filter(Product.bought.is_(False))

    min_cost = request.args.get("min_cost", type=float)
    max_cost = request.args.get("max_cost", type=float)
    cost_expr = Product.price * Product.quantity

    if min_cost is not None:
        query = query.filter(cost_expr >= min_cost)
    if max_cost is not None:
        query = query.filter(cost_expr <= max_cost)

    sort_by = request.args.get("sort_by")
    order = request.args.get("order", "asc")

    if sort_by == "name":
        sort_column = Product.name
    elif sort_by == "total_cost":
        sort_column = cost_expr
    elif sort_by == "bought":
        sort_column = Product.bought
    else:
        sort_column = None

    if sort_column is not None:
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    products = query.all()
    return jsonify([product.to_dict() for product in products]), 200

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return 'Product successfully deleted', 204

@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)

    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    product.category = CategoryEnum(data.get("category"))
    product.quantity = data.get("quantity", product.quantity)
    product.bought = data.get("bought", product.bought)

    db.session.commit()

    return jsonify({"message": "Product successfully updated"}), 200

if __name__ == "__main__":
    app.run()
