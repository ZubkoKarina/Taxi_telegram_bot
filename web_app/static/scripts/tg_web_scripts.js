let tg = window.Telegram.WebApp;
tg.expand();

document.querySelector('.order-button').addEventListener('click', () => {
    const from = document.getElementById('from').value;
    const fromLat = document.getElementById('from_lat').value;
    const fromLng = document.getElementById('from_lng').value;
    const to = document.getElementById('to').value;
    const toLat = document.getElementById('to_lat').value;
    const toLng = document.getElementById('to_lng').value;
    const taxiClassSelect = document.getElementById('class');
    const taxiClassId = taxiClassSelect.value;
    const taxiClassName = taxiClassSelect.options[taxiClassSelect.selectedIndex].text;
    const button_pay = document.getElementById('method_pay').value;
    const price = document.getElementById('output-cost').value;

    const comment = document.getElementById('comment').value;
    const animals_checkbox = document.getElementById('animals');
    const overall_cargo_checkbox = document.getElementById('overall_cargo');
    const delivery_checkbox = document.getElementById('delivery');
    const baby_chair_checkbox = document.getElementById('animals');

    let animals = false;
    let overall_cargo = false;
    let delivery = false;
    let baby_chair = false;
    if (animals_checkbox.checked) {
        animals = true
    }
    if (overall_cargo_checkbox.checked) {
        overall_cargo = true
    }
    if (delivery_checkbox.checked) {
        delivery = true
    }
    if (baby_chair_checkbox.checked) {
        baby_chair = true
    }

    if (!from || !to || !taxiClassId) {
        alert('Будь ласка, заповніть всі поля перед замовленням.');
        return;
    }
    const orderData = {
        chat_id: tg.initDataUnsafe.user.id,
        addressFrom: from,
        fromCoordinates: [fromLat, fromLng],
        addressTo: to,
        toCoordinates: [toLat, toLng],
        taxiClass: {
            id: taxiClassId,
            name: taxiClassName
        },
        payMethod: button_pay,
        price: price,
        otherSetting: {
            animals: animals,
            overall_cargo: overall_cargo,
            delivery: delivery,
            baby_chair: baby_chair,
            comment: comment,
        }
    };

    console.log('Sending order data:', orderData);
    fetch('/send_order_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    tg.close()

    function log(message) {
        fetch(`/log?message=${message}`)
    }
});
