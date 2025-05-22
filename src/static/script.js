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

        const editButton = document.createElement("button");
        editButton.textContent = "Edytuj";
        editButton.style.marginLeft = "10px";
        editButton.addEventListener("click", () => {
            li.innerHTML = '';

            const nameInput = document.createElement("input");nameInput.value = product.name;

            const priceInput = document.createElement("input");
            priceInput.type = "number";
            priceInput.step = "0.01";
            priceInput.value = product.price;

            const categoryInput = document.createElement("input");
            categoryInput.value = product.category;

            const quantityInput = document.createElement("input");
            quantityInput.type = "number";
            quantityInput.step = "1";
            quantityInput.value = product.quantity;

            const boughtInput = document.createElement("input");
            boughtInput.type = "checkbox";
            boughtInput.checked = product.bought;

            const saveButton = document.createElement("button");
            saveButton.textContent = "Zapisz";

            const cancelButton = document.createElement("button");
            cancelButton.textContent = "Anuluj";

            li.appendChild(nameInput);
            li.appendChild(priceInput);
            li.appendChild(categoryInput);
            li.appendChild(quantityInput);
            li.appendChild(boughtInput);
            li.appendChild(saveButton);
            li.appendChild(cancelButton);

            saveButton.addEventListener("click", () => {
                const updatedProduct = {
                    id: product.id,
                    name: nameInput.value,
                    price: priceInput.value,
                    category: categoryInput.value,
                    quantity: quantityInput.value,
                    bought: boughtInput.checked
                };

                updateProduct(updatedProduct).then(() => {
                    li.remove();
                    appendProduct(updatedProduct);
                });
            });

            cancelButton.addEventListener("click", () => {
                li.remove();
                appendProduct(product);
            });     
        });
        li.appendChild(deleteButton);
        li.appendChild(editButton);
        productsList.appendChild(li);
    }

    const updateProduct = async (product) => {
        const res = await fetch(`/api/products/${product.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(product),

        });
        
    }
});

