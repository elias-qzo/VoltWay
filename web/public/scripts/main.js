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


let carBrandSelect = document.getElementById("car-brand")
let carModelSelect = document.getElementById("car-model")
carModelSelect.style.display = "none"
let carData = []

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
    carAutonomyInfo.innerHTML = `Autonomie : ${carData['autonomy']} mn`
    carChargetimeInfo.innerHTML = `Temps de charge : ${carData['charge-time']} mn`
}

carModelSelect