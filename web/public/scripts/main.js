const api = axios.create({
    baseURL: 'http://127.0.0.1:6060',
    timeout: 0,
});

const map = L.map('map').setView([46.603354, 1.888334], 6);
const originInput = document.getElementById("origin-input")
const destinationInput = document.getElementById("destination-input")
const travelButton = document.getElementById("travel-button")

const travelDetails = document.getElementById("travel-infos")
travelDetails.style.display = "none"
const travelTime = document.getElementById("travel-time")
const travelCost = document.getElementById("travel-cost")
const travelDistance = document.getElementById("travel-distance")


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

/* TRAVEL */

let routeLayerGroup = L.layerGroup().addTo(map);

function setTravel(tripWaypoints, chargingStations) {
    routeLayerGroup.clearLayers();

    if (tripWaypoints.length < 2) return;

    let waypoints = tripWaypoints.map(waypoint => L.latLng(waypoint[1], waypoint[0]));

    for (let i = 0; i < waypoints.length - 1; i++) {
        let polyline = L.polyline([waypoints[i], waypoints[i + 1]], {
            color: '#4275f5',
            weight: 3
        }).addTo(routeLayerGroup);
    }

    L.marker(waypoints[0], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(routeLayerGroup).bindPopup("Point de départ");

    if (tripWaypoints.length > 1) {
        L.marker(waypoints[waypoints.length - 1], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(routeLayerGroup).bindPopup("Destination");
    }

    chargingStations.forEach(station => {
        L.marker([station[1], station[0]], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(routeLayerGroup);
    });
}

function formatSecondsToHours(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h${minutes.toString().padStart(2, '0')}`;
}

function setTravelDetails(travel){
    travelDetails.style.display = "inline"
    travelDistance.innerHTML = "Distance : "+Math.floor(travel.summary.distance / 1000) + " km"
    travelCost.innerHTML = "Coût : "+travel.summary.cost+ " €"
    travelTime.innerHTML = "Durée : "+formatSecondsToHours(travel.summary.duration)

}

travelButton.addEventListener("click",function(){
    if (Object.keys(selectedCarData).length === 0) {
        alert("Vous devez choisir un véhicule")
        return
    }
    
    let params = {
        "origin": originInput.value,
        "destination": destinationInput.value,
        "autonomy": selectedCarData['autonomy'],
        "load_time": selectedCarData['charge-time']
    }
    api.get('/itinerary', { params })
    .then(response => {
        console.log(response.data);
        setTravel(response.data["waypoints"],response.data["charging_stations"])
        setTravelDetails(response.data)
    })
    .catch(error => {
        console.error("Error :", error);
    });
})

/* CAR SELECTION */

let carBrandSelect = document.getElementById("car-brand")
let carModelSelect = document.getElementById("car-model")
carModelSelect.style.display = "none"
let carData = []
let selectedCarData = {}


carBrandSelect.addEventListener("change", function () {
    if(carBrandSelect.value == "default"){
        carModelSelect.style.display = "none"
    } else {
        carModelSelect.style.display = "flex";
        let params = {
            "brand": carBrandSelect.value,
        }

        api.get('/vehicles', { params })
        .then(response => {
            carData = response.data
            initModelSelect()
            console.log(response.data);
        })
        .catch(error => {
            console.error("Error :", error);
        });
    }
});

carModelSelect.addEventListener("change", function () {
    if(carModelSelect.value == "default"){
        carInfosContainer.style.display = "none"
    } else {
        selectedCarData = carData[carModelSelect.value]
        initCarInfo(carData[carModelSelect.value])
    }
})

function create(tagName, container, text = null, classs = null, id = null) {
    let element = document.createElement(tagName)
    container.appendChild(element)
    if (text)
        element.appendChild(document.createTextNode(text))
    if (classs)
        element.classList.add(classs)
    if (id)
        element.id = id
    return element
}

function initModelSelect(){
    while (carModelSelect.firstChild) {
        carModelSelect.removeChild(carModelSelect.firstChild);
    }
    create("option",carModelSelect,"Choississez un model",id="default")
    for(let i = 0; i < carData.length; i++){
        let model = create("option",carModelSelect,carData[i]['model'])
        model.value = i
    }
}

let carInfosContainer = document.getElementById("car-infos")
carInfosContainer.style.display = "none"

let carImage = document.getElementById("car-image")
let carModelInfo = document.getElementById("car-model-info")
let carAutonomyInfo = document.getElementById("car-autonomy-info")
let carChargetimeInfo = document.getElementById("car-chargetime-info")

function initCarInfo(carData){
    carInfosContainer.style.display = "inline"
    carImage.src = carData['image']
    carModelInfo.innerHTML = `${carData['brand']} ${carData['model']}`
    carAutonomyInfo.innerHTML = `Autonomie : ${carData['autonomy']} km`
    carChargetimeInfo.innerHTML = `Temps de charge : ${carData['charge-time']} mn`
}
