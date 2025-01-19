const api = axios.create({
    baseURL: 'http://127.0.0.1:6060',
    timeout: 5000,
});

const map = L.map('map').setView([46.603354, 1.888334], 6);
const originInput = document.getElementById("origin-input")
const destinationInput = document.getElementById("destination-input")
const travelButton = document.getElementById("travel-button")

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

function setTravel(origin, destination) {
    if (window.currentRouteControl) {
        map.removeControl(window.currentRouteControl);
    }

    window.currentRouteControl = L.Routing.control({
        waypoints: [
            L.latLng(origin["lat"], origin["lon"]),
            L.latLng(destination["lat"], destination["lon"])
        ],
        routeWhileDragging: false,
        show: false, 
        addWaypoints: false,
        lineOptions: {
            styles: [{ color: '#4275f5', weight: 3 }]
        }
    }).addTo(map);
}


travelButton.addEventListener("click",function(){
    let params = {
        "origin": originInput.value,
        "destination": destinationInput.value
    }
    api.get('/itinerary', { params })
    .then(response => {
        console.log(response.data);
        setTravel(response.data["origin"],response.data["destination"])
    })
    .catch(error => {
        console.error("Error :", error);
    });
})
