function generateItems(n){
    let container = document.getElementById("items_container");
    container.innerHTML = "";
    if (!n || n < 1) return;
    for(let i=0;i<n;i++){
      let div = document.createElement("div");
      div.className = "purchase-item-row";
      div.innerHTML = `
        <div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:10px">
          <input placeholder="Item Name" name="items-${i}-item_name" style="flex:1" />
          <input placeholder="Link (required)" name="items-${i}-link" style="flex:2" required />
          <input placeholder="Unit Price" name="items-${i}-unit_price" type="number" step="0.01" style="flex:1" />
          <input placeholder="Quantity" name="items-${i}-quantity" type="number" min="1" value="1" style="flex:1" />
        </div>
      `;
      container.appendChild(div);
    }
  }

  function validatePurchaseForm(){
    const numItems = Number(document.getElementById("num_items").value);
    if (numItems < 1) {
      alert("Please enter at least 1 item");
      return false;
    }
    // Check that each item has a non-empty link field (required for validation)
    for (let i = 0; i < numItems; i++) {
      const linkInput = document.querySelector(`input[name="items-${i}-link"]`);
      const quantityInput = document.querySelector(`input[name="items-${i}-quantity"]`);
      if (!linkInput || !linkInput.value.trim()) {
        alert(`Item ${i+1} is missing a link. Please fill in all item links.`);
        linkInput?.focus();
        return false;
      }
      // Ensure quantity is a valid positive integer
      const qty = quantityInput?.value;
      if (qty && (isNaN(qty) || parseInt(qty) < 1)) {
        alert(`Item ${i+1} quantity must be at least 1.`);
        quantityInput?.focus();
        return false;
      }
    }
    return true;
  }
  