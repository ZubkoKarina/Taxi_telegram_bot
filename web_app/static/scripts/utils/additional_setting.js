document.getElementById('method_pay').addEventListener('click', function() {
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

document.getElementById('change_cost').addEventListener('click', function() {
    const price = parseFloat(document.getElementById('output-cost').value);

    const addressModal = document.getElementById("changePrice");
    addressModal.style.display = "block";
    addressModal.classList.add('fade-in');

    const modalContent = document.querySelector('.price-modal-content');
    modalContent.classList.add('slide-up');
    const input_change_price = document.getElementById('changePriceInput');
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = price + ' ₴';
    input_change_price.value = price;
    input_change_price.min = price;
    input_change_price.max = price * 2;
});

document.getElementById('changePriceInput').addEventListener('input', function() {
    const changePriceInput = document.getElementById("changePriceInput");
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = changePriceInput.value + ' ₴';
});

document.getElementById('savePriceButton').addEventListener('click', function() {
    const changePriceInput = document.getElementById("changePriceInput");
    const newPrice = changePriceInput.value;

    document.getElementById('output-cost').value = newPrice;
    document.getElementById('output-cost').textContent = `${newPrice} грн`;

    const addressModal = document.getElementById("changePrice");
    addressModal.style.display = "none";
});

document.getElementById('bt_additional_service').addEventListener('click', function() {
    const addressModal = document.getElementById("otherSetting");
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


document.getElementById('saveSettingButton').addEventListener('click', function() {
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

    settingModal = document.getElementById('otherSetting')

    settingModal.dataset.comment = full_comment
    settingModal.style.display = 'none';
});

document.getElementById('bt_comment').addEventListener('click', function() {
    const Modal = document.getElementById("commentModal");
    Modal.style.display = "block";

    addressModal.classList.add('slide-up');
});


document.getElementById('saveCommentButton').addEventListener('click', function() {
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

    Modal = document.getElementById('commentModal')

    Modal.dataset.comment = full_comment
    Modal.style.display = 'none';
});

