let tg = window.Telegram.WebApp;
tg.expand();

document.querySelector('.order-button').addEventListener('click', () => {
    const from = document.getElementById('from').value;
    const fromLat = document.getElementById('from_lat').value;
    const fromLng = document.getElementById('from_lng').value;
    const to = document.getElementById('to').value;
    const toLat = document.getElementById('to_lat').value;
    const toLng = document.getElementById('to_lng').value;
    const taxiClass = document.getElementById('class').value;
    const button_pay = document.getElementById('method_pay').value;
    const price = document.querySelector('.order-button').value

    if (!from || !to || !taxiClass) {
        alert('Будь ласка, заповніть всі поля перед замовленням.');
        return;
    }
    const orderData = {
        addressFrom: from,
        fromCoordinates: [fromLat, fromLng],
        addressTo: to,
        toCoordinates: [toLat, toLng],
        taxiClass: taxiClass,
        payMethod: button_pay,
        price: price,
    };

    console.log('Sending order data:', orderData);
    tg.sendData(JSON.stringify(orderData));
});
