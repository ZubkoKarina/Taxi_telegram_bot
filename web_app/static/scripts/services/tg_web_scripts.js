let tg = window.Telegram.WebApp;
tg.expand();

document.getElementById('accept_order').addEventListener('click', () => {
    const from = document.getElementById('from').dataset.id;
    const fromLat = document.getElementById('from_lat').value;
    const fromLng = document.getElementById('from_lng').value;
    const to = document.getElementById('to').dataset.id;
    const toLat = document.getElementById('to_lat').value;
    const toLng = document.getElementById('to_lng').value;
    const taxiClassBlockActive = document.querySelector('.block-taxi-class.selected');
    const taxiClassId = taxiClassBlockActive.dataset.id;
    const taxiClassName = taxiClassBlockActive.dataset.name;
    const button_pay = document.getElementById('method_pay').value;
    const price = document.getElementById('output-cost').value;
    const comment = document.getElementById('otherSetting').dataset.comment;

    if (!from || !to || !taxiClassId) {
        showNotification('Будь ласка, заповніть всі поля перед замовленням.');
        return;
    }

    if (button_pay === 'Карта') {
        fetch('/online_payment', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (!data) {
                showNotification('Наразі оплата карткою не доступна');
                return;
            } else {
                sendOrderData({
                    chat_id: tg.initDataUnsafe.user.id,
                    idFrom: from,
                    fromCoordinates: [fromLat, fromLng],
                    idTo: to,
                    toCoordinates: [toLat, toLng],
                    taxiClass: {
                        id: taxiClassId,
                        name: taxiClassName
                    },
                    payMethod: button_pay,
                    price: price,
                    comment: comment,
                });
            }
        })
        .catch(error => {
            console.error('Error checking online payment:', error);
        });
    } else {
        sendOrderData({
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
            comment: comment,
        });
    }
});

function sendOrderData(orderData) {
    console.log('Sending order data:', orderData);
    fetch('/send_order_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .then(response => {
        tg.close();
    })
    .catch(error => {
        console.error('Error sending order data:', error);
    });
}

function log(message) {
    fetch(`/log?message=${message}`);
}

function showNotification(textNotification) {
    const notification = document.getElementById('notification');
    const textNotificationElement = document.getElementById('text-notification');
    textNotificationElement.textContent = textNotification
    notification.classList.add('show');
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

