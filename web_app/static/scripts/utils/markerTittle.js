class CustomInfoWindow extends google.maps.OverlayView {
    constructor(position, content) {
        super();
        this.position = position;
        this.content = content;
        this.div = null;
    }

    onAdd() {
        const div = document.createElement('div');
        div.style.position = 'absolute';
        div.innerHTML = this.content;

        div.style.background = 'white';
        div.style.borderRadius = '6px';
        div.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
        div.style.zIndex = '1000';
        div.style.pointerEvents = 'auto';

        this.div = div;
        const panes = this.getPanes();
        panes.overlayLayer.appendChild(div);
        div.style.transform = 'translate(0%, -150%)';
    }

    draw() {
        const overlayProjection = this.getProjection();
        const position = overlayProjection.fromLatLngToDivPixel(this.position);

        if (this.div) {
            this.div.style.left = position.x + 13 + 'px';
            this.div.style.top = position.y + 'px';
        }
    }

    onRemove() {
        if (this.div) {
            this.div.parentNode.removeChild(this.div);
            this.div = null;
        }
    }

    hide() {
        if (this.div) {
            this.div.style.display = 'none';
        }
    }

    show() {
        if (this.div) {
            this.div.style.display = 'block';
        }
    }
}

function addTittle(marker) {
    let number = 0;
    let address = 'Адреса не знайдена';
    let searchInputElement = document.getElementById(currentInputId);
    let contentString = null;

    if (currentInputId === 'add-stop-button') {
        let addressList = JSON.parse(searchInputElement.dataset.addressList);
        number = addressList.length;
        let lastAddress = addressList[addressList.length - 1];
        address = lastAddress.address;
    }
    if (currentInputId === 'to') {
        number = '<i class="fa-solid fa-arrow-up-long"></i>';
        address = searchInputElement.value;
    }
    if (markers.length == 1) {
        searchInputElement = document.getElementById('from');
        number = '<i class="fa-solid fa-arrow-down"></i>';
        address = searchInputElement.value;
    }

    contentString = `
        <div id="custom-info-window">
            <div class='tittle-marker-number'>${number}</div>
            <div id="tittle-marker-address">${address}</div>
        </div>
    `;

    const infoWindow = new CustomInfoWindow(marker.getPosition(), contentString);
    infoWindow.setMap(map);

    // Зберігаємо інфовікно разом з маркером
    marker.infoWindow = infoWindow;
}

