let currentListId = null;
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const nameInput = document.getElementById("nameInput");
    const priceInput = document.getElementById("priceInput");
    const categoryInput = document.getElementById("categoryInput");
    const quantityInput = document.getElementById("quantityInput");
    const productsList = document.getElementById("productsList");
    const listForm = document.getElementById("listForm");
    const listNameInput = document.getElementById("listNameInput");
    const listSelect = document.getElementById("listSelect");
    

    listForm.addEventListener("submit", (e) =>{
        e.preventDefault();

        const newList = {
            name: listNameInput.value
        }; 

        fetch("/api/lists", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newList)
        }).then(res => res.json())
        .then(data => {
            const option = document.createElement("option");
            option.value = data.id;
            const date = new Date(data.created_at);
            const formatted = date.toLocaleString(); 
            option.textContent = `${data.name} (${formatted})`;
            listSelect.appendChild(option);
            currentListId = data.id;
            data.products.forEach(appendProduct);
        })
    })

    listSelect.addEventListener("change", (e) => {
        e.preventDefault();
        const id = listSelect.value;

        fetch(`/api/lists/${id}`)
            .then(res => res.json()
            .then(data => {
                productsList.innerHTML = "";
                currentListId = data.id;
                data.products.forEach(appendProduct);
            })
        );
    })

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const newProduct = {
            name: nameInput.value,
            price: priceInput.value,
            category: categoryInput.value,
            quantity: quantityInput.value,
            listId: currentListId
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

    const filterForm = document.getElementById("filterForm");
    const minCost = document.getElementById("minCost");
    const maxCost = document.getElementById("maxCost");
    const filterCategory = document.getElementById("filterCategory");
    const filterBought = document.getElementById("filterBought");

    filterForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const query = new URLSearchParams();
        if (minCost.value) query.append("min_cost", minCost.value);
        if (maxCost.value) query.append("max_cost", maxCost.value);
        if (filterCategory.value) query.append("category", filterCategory.value);
        if (filterBought.value) query.append("bought", filterBought.value);
        if (currentListId) query.append("listId", currentListId);

        fetch(`/api/products?${query.toString()}`)
            .then(res => res.json())
            .then(data => {
                productsList.innerHTML = "";
                data.forEach(appendProduct);
            })
            .catch(err => console.error("Błąd filtrowania:", err));
    });

    const sortForm = document.getElementById("sortForm");
    const sortBy = document.getElementById("sortBy");
    const sortOrder = document.getElementById("sortOrder");

    sortForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const query = new URLSearchParams();
        if (sortBy.value) query.append("sort_by", sortBy.value);
        if (sortOrder.value) query.append("order", sortOrder.value);
        if (currentListId) query.append("listId", currentListId);

        fetch(`/api/products?${query.toString()}`)
            .then(res => res.json())
            .then(data => {
                productsList.innerHTML = "";
                data.forEach(appendProduct);
            })
            .catch(err => console.error("Błąd sortowania:", err));
    });


    function appendProduct(product) {
        const li = document.createElement("li");
        let formatted = "";

        if (product.bought) {
            const date = new Date(product.when_bought);
            const formatted_date = date.toLocaleString();
            formatted = `(${formatted_date})`;
        }
        li.textContent = `${product.name} - ${product.price} zł [${product.category}] - ${product.quantity} sztuki - ${(product.price * product.quantity).toFixed(2)} zł - ${product.bought ? "Kupiony" : "Nie kupiony"} ${formatted}`;

        //po dodaniu produktu, dodanie przycisku do usuwania 
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Usuń";
        deleteButton.style.marginLeft = "10px";

        deleteButton.addEventListener("click", () => {
            fetch(`/api/products/${product.id}`, {
                method: "DELETE"
            }).then(res => {
                if (res.ok) {
                    li.remove();

                } else {
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

            const nameInput = document.createElement("input");
            nameInput.value = product.name;

            const priceInput = document.createElement("input");
            priceInput.type = "number";
            priceInput.step = "0.01";
            priceInput.value = product.price;

            const categoryInput = document.createElement("select");
            ["Warzywa", "Owoce", "Nabiał", "Pieczywo", "Napoje", "Inne"].forEach(cat => {
                const opt = document.createElement("option");
                opt.value = cat;
                opt.textContent = cat.charAt(0) + cat.slice(1).toLowerCase();
                if (cat === product.category.toUpperCase()) opt.selected = true;
                categoryInput.appendChild(opt);
            });

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
                    price: parseFloat(priceInput.value),
                    category: categoryInput.value,
                    quantity: parseInt(quantityInput.value),
                    bought: boughtInput.checked,
                    listId: currentListId
                };

                updateProduct(updatedProduct).then((newProduct) => {
                    if (newProduct) {
                        li.remove();
                        appendProduct(newProduct); 
                    }
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
    try {
        const res = await fetch(`/api/products/${product.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(product),
        });

        if (!res.ok) {
            throw new Error("Błąd podczas aktualizacji produktu");
        }

        const updated = await res.json(); 
        return updated;
    } catch (err) {
        console.error("Błąd:", err);
        return null;
    }
};


});

function analysis() {
    fetch(`api/analysis/${currentListId}`).then(res => {
        if (!res.ok) {
                return res.json().then(err => Promise.reject(err));
            }
            return res.json();
        }).then(data => {
        const container = document.getElementById("analysisContainer");
        container.innerHTML = `<h3>Średnia cena produktów wg kategorii</h3>
        <img src="data:image/png;base64,${data.chart}" alt="Wykres kategorii" />
        <button id="backBtn">Powrót</button>
        `;
        document.getElementById("backBtn").addEventListener("click", returnToMainView);
    }).catch(error => {
            const container = document.getElementById("analysisContainer");
            container.innerHTML = `<p style="color:red;">Błąd: ${error.error || "Nieznany błąd"}</p>`;
        });
}
function returnToMainView() {
    document.getElementById("analysisContainer").innerHTML = "";
}

analysisBtn.addEventListener("click", () => {
    analysis(currentListId);
});