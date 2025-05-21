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
    bought = db.Column(db.Boolean, nullable=False)

    def __init__(self, name, price, category, bought=False):
        self.name = name
        self.price = float(price)
        self.category = category
        self.bought = bought

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "bought": self.bought
        }


with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/products", methods=["GET", "POST"])
def handle_products():
    if request.method == "POST":
        data = request.get_json()
        attributes_string = data.get("productAtributes", "")
        attributes_arr = attributes_string.split(",")

        if len(attributes_arr) < 3:
            return jsonify({"error": "Invalid product data"}), 400

        new_product = Product(
            name=attributes_arr[0].strip(),
            price=attributes_arr[1].strip(),
            category=attributes_arr[2].strip(),
            bought=False
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
