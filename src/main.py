from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    bought = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
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
        category = data.get("category")

        if not name or not price or not category:
            return jsonify({"error": "Missing product data"}), 400

        new_product = Product(
            name=name.strip(),
            price=float(price),
            category=category.strip()
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

if __name__ == "__main__":
    app.run(debug=True)
