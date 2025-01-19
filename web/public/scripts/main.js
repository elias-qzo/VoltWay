const map = L.map('map').setView([46.603354, 1.888334], 6);

// Ajouter les tuiles OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Ajouter un trajet avec Leaflet Routing Machine
L.Routing.control({
    waypoints: [
        L.latLng(48.8566, 2.3522), // Point de départ : Paris
        L.latLng(43.6047, 1.4442)  // Point d'arrivée : Toulouse
        ],
    routeWhileDragging: false,
    show: false,
    addWaypoints: false,
    lineOptions: {
        styles: [{ color: '#c71f1f', weight: 3 }]
    }
}).addTo(map);