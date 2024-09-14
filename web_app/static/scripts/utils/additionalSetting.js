document.getElementById('payment-method-button').addEventListener('click', function() {
    const button = this;
    const ico = document.getElementById('payIco');

    if (button.value === 'Готівка') {
        button.value = 'Карта';
        ico.className = 'bi bi-credit-card-2-front';
        button.innerHTML = '<i class="bi bi-credit-card-2-front" id="payIco"></i><br>Карта';
    } else {
        button.value = 'Готівка';
        ico.className = 'bi bi-cash';
        button.innerHTML = '<i class="bi bi-cash" id="payIco"></i><br>Готівка';
    }
});

document.getElementById('change-price-button').addEventListener('click', function() {
    const price = parseFloat(document.getElementById('output-cost').value);

    const addressModal = document.getElementById("price-modal");
    addressModal.style.display = "block";
    addressModal.classList.add('fade-in');

    const modalContent = document.querySelector('.price-modal-content');
    modalContent.classList.add('slide-up');
    const input_change_price = document.getElementById('price-slider');
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = price + ' ₴';
    input_change_price.value = price;
    input_change_price.min = price;
    input_change_price.max = price * 2;
});

document.getElementById('price-slider').addEventListener('input', function() {
    const changePriceInput = document.getElementById("price-slider");
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = changePriceInput.value + ' ₴';
});

document.getElementById('confirm-price-button').addEventListener('click', function() {
    const changePriceInput = document.getElementById("price-slider");
    const newPrice = changePriceInput.value;

    document.getElementById('output-cost').value = newPrice;
    document.getElementById('output-cost').textContent = `${newPrice} грн`;

    const addressModal = document.getElementById("price-modal");
    addressModal.style.display = "none";
});

document.getElementById('additional-services-button').addEventListener('click', function() {
    const addressModal = document.getElementById("additional-settings-modal");
    addressModal.style.display = "block";

    addressModal.classList.add('slide-up');
});

function updatePrice(button) {
    const outputCostElement = document.getElementById('output-cost');
    const outputCost = parseFloat(outputCostElement.value) || 0;
    const serviceCost = parseFloat(button.dataset.cost);
    alert(serviceCost)

    let totalCost = outputCost;

    if (!outputCostElement.dataset.costRoad) {
        totalCost = serviceCost;
    } else {
        totalCost = parseFloat(outputCostElement.dataset.costRoad) + serviceCost;
    }

    outputCostElement.dataset.costServices = serviceCost;
    outputCostElement.value = totalCost;
    outputCostElement.textContent = `${totalCost} грн`;
}


document.getElementById('confirm-settings-button').addEventListener('click', function() {
    const selectedServices = [];
    let additionalCost = 0;
    const outputCostElement = document.getElementById('output-cost');
    const outputCost = parseFloat(outputCostElement.value) || 0;

    document.querySelectorAll('.additional-services button.selected').forEach(button => {
        selectedServices.push(button.value + '❗️\n');
        additionalCost += parseFloat(button.dataset.cost);
    });

    const comment_text = document.getElementById('comment').value;
    let full_comment = selectedServices + 'Коментарій: ' + comment_text;

    console.log('Збережені налаштування:', full_comment);

    let totalCost = outputCost;

    if (!outputCostElement.dataset.costRoad) {
        totalCost = additionalCost;
    } else {
        totalCost = parseFloat(outputCostElement.dataset.costRoad) + additionalCost;
    }

    outputCostElement.dataset.costServices = additionalCost;
    outputCostElement.value = totalCost;
    outputCostElement.textContent = `${totalCost} грн`;

    settingModal = document.getElementById('additional-settings-modal')

    settingModal.dataset.comment = full_comment

    settingModal.classList.remove('slide-up')
    settingModal.classList.add('folding-down')
    setTimeout(() => {
        settingModal.style.display = 'none';
        settingModal.classList.remove('folding-down')
    }, 200);
});

document.getElementById('comment-button').addEventListener('click', function() {
    const Modal = document.getElementById("comment-modal");
    const content = document.querySelector(".comment-content");
    Modal.style.display = "block";

    content.classList.add('slide-up')
    Modal.classList.add('fade-in');
});


document.getElementById('save-comment-button').addEventListener('click', function() {
    const selectedServices = [];
    let additionalCost = 0;
    const outputCostElement = document.getElementById('output-cost');
    const outputCost = parseFloat(outputCostElement.value) || 0;

    document.querySelectorAll('.additional-services button.selected').forEach(button => {
        selectedServices.push(button.value + '❗️\n');
        additionalCost += parseFloat(button.dataset.cost);
    });

    const comment_text = document.getElementById('comment').value;
    let full_comment = selectedServices + '\n' + comment_text;

    console.log('Збережені налаштування:', full_comment);

    let totalCost = outputCost;

    if (!outputCostElement.dataset.costRoad) {
        totalCost = additionalCost;
    } else {
        totalCost = parseFloat(outputCostElement.dataset.costRoad) + additionalCost;
    }

    outputCostElement.dataset.costServices = additionalCost;
    outputCostElement.value = totalCost;
    outputCostElement.textContent = `${totalCost} грн`;

    const Modal = document.getElementById('comment-modal')
    const content = document.querySelector(".comment-content");

    Modal.dataset.comment = full_comment

    content.classList.remove('slide-up')
    Modal.classList.remove('fade-in');
    content.classList.add('folding-down')
    Modal.classList.add('fade-out');
    setTimeout(() => {
        Modal.style.display = 'none';
        content.classList.remove('folding-down')
        Modal.classList.remove('fade-out');
    }, 200);
});

document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('focus', function() {
        setTimeout(() => {
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100); // Невелика затримка для появи клавіатури
    });
});
