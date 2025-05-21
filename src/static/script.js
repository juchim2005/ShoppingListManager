document.addEventListener("DOMContentLoaded", () => {
    const productForm = document.getElementById("productForm");
    const productInput = document.getElementById("productInput");
    const productsList = document.getElementById("productsList");

    productForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const productAtributes = productInput.value;
        
        fetch("/api/products", {
            method: "POST", 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({productAtributes}),
        })
        .then((response) => response.json())
        .then((data) => console.log(data))
        .catch((error) => console.error(error));
    });
});