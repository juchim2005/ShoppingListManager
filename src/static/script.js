document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const nameInput = document.getElementById("nameInput");
    const priceInput = document.getElementById("priceInput");
    const categoryInput = document.getElementById("categoryInput");
    const quantityInput = document.getElementById("quantityInput");
    const productsList = document.getElementById("productsList");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const newProduct = {
            name: nameInput.value,
            price: priceInput.value,
            category: categoryInput.value,
            quantity: quantityInput.value
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
        li.textContent = `${product.name} - ${product.price} zł [${product.category}] - ${product.quantity} sztuki - ${product.price * product.quantity} zł - ${product.bought ? "Kupiony" : "Nie kupiony"}`;
        productsList.appendChild(li);

        //po dodaniu produktu, dodanie przycisku do usuwania 
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Usuń";
        deleteButton.style.marginLeft = "10px";

        deleteButton.addEventListener("click", () => {
            fetch(`/api/products/${product.id}`, {
                method: "DELETE"
        }).then(res => {
            if(res.ok) {
                li.remove();
                
            }else{
                console.error("Błąd podczas usuwania produktu");
            }
        })
        .catch(err => console.error("Błąd:", err)); 
        });

        li.appendChild(deleteButton);
    }
});

