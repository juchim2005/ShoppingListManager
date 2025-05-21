document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const nameInput = document.getElementById("nameInput");
    const priceInput = document.getElementById("priceInput");
    const categoryInput = document.getElementById("categoryInput");
    const productsList = document.getElementById("productsList");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const newProduct = {
            name: nameInput.value,
            price: priceInput.value,
            category: categoryInput.value
        };

        fetch("/api/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newProduct)
        })
        .then(res => res.json())
        .then(data => {
            appendProduct(data);
            form.reset();
        })
        .catch(err => console.error("Błąd:", err));
    });

    // Wczytaj istniejące produkty
    fetch("/api/products")
        .then(res => res.json())
        .then(data => data.forEach(appendProduct))
        .catch(err => console.error("Błąd:", err));

    function appendProduct(product) {
        const li = document.createElement("li");
        li.textContent = `${product.name} - ${product.price} zł [${product.category}]`;
        productsList.appendChild(li);
    }
});