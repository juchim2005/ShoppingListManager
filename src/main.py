from enum import Enum
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import func

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.typing import ResponseReturnValue
import os
import matplotlib
matplotlib.use('Agg')  

import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import io
import base64

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


class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', back_populates='shopping_list', lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "products": [product.to_dict() for product in self.products]
        }


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(SqlEnum(CategoryEnum), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    bought = db.Column(db.Boolean, default=False, nullable=False)
    when_bought = db.Column(db.DateTime, default=None, nullable=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'), nullable=False)
    shopping_list = db.relationship('ShoppingList', back_populates='products')

    def set_date(self, ifbought: bool) -> None:
        if ifbought:
            self.when_bought = datetime.utcnow()
        else:
            self.when_bought = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category.value,
            "quantity": self.quantity,
            "bought": self.bought,
            "when_bought": self.when_bought
        }


with app.app_context():
    db.create_all()


@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/api/lists", methods=["GET", "POST"])
def handle_lists() -> ResponseReturnValue:
    if request.method == "POST":
        data: Dict[str, Any] = request.get_json()
        name: Optional[str] = data.get("name")
        if not name:
            return jsonify({"error": "Missing list data"}), 400

        new_list = ShoppingList(name=name)
        db.session.add(new_list)
        db.session.commit()
        return jsonify(new_list.to_dict()), 201

    lists: List[ShoppingList] = ShoppingList.query.all()
    return jsonify([list.to_dict() for list in lists]), 200


@app.route("/api/lists/<int:id>", methods=["GET"])
def find_list(id: int) -> ResponseReturnValue:
    list_ = ShoppingList.query.get_or_404(id)
    return jsonify(list_.to_dict()), 200


@app.route("/api/lists/czemutoniedziala", methods=["GET"])
def get_shopping_lists_names() -> ResponseReturnValue:
    lists: List[ShoppingList] = ShoppingList.query.all()
    return jsonify([{"id": list_.id, "name": list_.name, "created_at": list_.created_at} for list_ in lists]), 200


@app.route("/api/products", methods=["GET", "POST"])
def handle_products() -> ResponseReturnValue:
    if request.method == "POST":
        data: Dict[str, Any] = request.get_json()
        name: Optional[str] = data.get("name")
        price = data.get("price")
        category = CategoryEnum(data.get("category"))
        quantity = data.get("quantity")
        shopping_list_id = data.get("listId")

        if not name or not price or not category:
            return jsonify({"error": "Missing product data"}), 400

        new_product = Product(
            name=name.strip(),
            price=float(price),
            category=category,
            quantity=int(quantity),
            shopping_list_id=shopping_list_id
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    query = Product.query

    category_param = request.args.get("category")
    if category_param:
        try:
            query = query.filter(Product.category == CategoryEnum(category_param))
        except ValueError:
            return jsonify({"error": f"Invalid category: {category_param}"}), 400

    bought = request.args.get("bought")
    if bought is not None:
        if bought.lower() == "true":
            query = query.filter(Product.bought.is_(True))
        elif bought.lower() == "false":
            query = query.filter(Product.bought.is_(False))

    min_cost: Optional[float] = request.args.get("min_cost", type=float)
    max_cost: Optional[float] = request.args.get("max_cost", type=float)
    cost_expr = Product.price * Product.quantity

    if min_cost is not None:
        query = query.filter(cost_expr >= min_cost)
    if max_cost is not None:
        query = query.filter(cost_expr <= max_cost)

    sort_by = request.args.get("sort_by")
    order = request.args.get("order", "asc")

    sort_column = None
    if sort_by == "name":
        sort_column = Product.name
    elif sort_by == "total_cost":
        sort_column = cost_expr
    elif sort_by == "bought":
        sort_column = Product.bought

    if sort_column is not None:
        query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    list_id = request.args.get("listId", type=int)
    products: List[Product] = query.filter(Product.shopping_list_id == list_id).all()
    return jsonify([product.to_dict() for product in products]), 200


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> ResponseReturnValue:
    product: Optional[Product] = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return 'Product successfully deleted', 204


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int) -> ResponseReturnValue:
    data: Dict[str, Any] = request.get_json()
    product: Product = Product.query.get_or_404(product_id)

    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    product.category = CategoryEnum(data.get("category"))
    product.quantity = data.get("quantity", product.quantity)
    product.bought = data.get("bought", product.bought)
    product.set_date(product.bought)

    db.session.commit()
    return jsonify(product.to_dict()), 200

@app.route("/api/analysis/<int:currentListId>", methods=["GET"])
def analysis(currentListId: int):
    if not currentListId:
        return jsonify({"error": "Brak ID listy zakupów"}), 400
    data = db.session.query(Product.category, func.sum(Product.price * Product.quantity)).filter(Product.shopping_list_id == currentListId).group_by(Product.category).all()

    labels = [str(row[0].value) for row in data]
    values = [float(row[1])  for row in data]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("Całkowita cena produktów w danej kategorii")
    ax.set_xlabel("Kategoria")
    ax.set_ylabel("Koszt")
    ax.set_xticklabels(labels, rotation=45, ha='right')

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)

    return jsonify({"chart": img_base64})


if __name__ == "__main__":
    app.run()
