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
    const price = document.querySelector('.order-button').value

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
