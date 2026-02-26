// Bus.js - Handles live tracking and UI updates

// Firebase real-time location listener will be attached after login
//let currentUser = null;
//let userBus = null;
//let map = null;
//let busMarker = null;

// Initialize map view
function initMap() {
    map = L.map('map').setView([16.7, 81.1], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    L.marker([16.696499056086402, 81.05052784442461])
        .addTo(map)
        .bindPopup("<b>College Campus</b><br>Destination point for all buses");
}

// Update the bus marker position
function updateBusMarker() {
    if (!userBus || !userBus.currentLocation) return;

    if (busMarker) {
        map.removeLayer(busMarker);
    }

    busMarker = L.marker([userBus.currentLocation.lat, userBus.currentLocation.lng], {
        icon: L.divIcon({
            className: 'bus-marker',
            html: userBus.id || '',
            iconSize: [24, 24]
        })
    }).addTo(map);

    busMarker.bindPopup(`
        <div class="space-y-1">
            <h3 class="font-bold text-lg">${userBus.number}</h3>
            <p class="text-sm">${userBus.route}</p>
            <p class="text-sm"><span class="font-medium">Driver:</span> ${userBus.driver}</p>
            <p class="text-sm"><span class="font-medium">Status:</span> ${userBus.status}</p>
            <p class="text-sm"><span class="font-medium">ETA:</span> ${userBus.eta}</p>
            <p class="text-sm"><span class="font-medium">Stop:</span> ${userBus.currentStop}</p>
        </div>
    `);

    map.setView([userBus.currentLocation.lat + 0.01, userBus.currentLocation.lng], 13);
}

// After login, attach the Firebase listener
function startTracking(busId) {
    const busLocationRef = firebase.database().ref("buses/bus" + busId + "/location");
    busLocationRef.on("value", (snapshot) => {
        if (snapshot.exists()) {
            const loc = snapshot.val();

            console.log("📍 Firebase changed:", loc);

           
            if (!userBus.currentLocation) userBus.currentLocation = {};
            userBus.currentLocation.lat = loc.lat;
            userBus.currentLocation.lng = loc.lng;
            
            // ✅ Add this line
            console.log("🚍 Updating marker at:", userBus.currentLocation);

            updateBusMarker();
            updateLastUpdatedTime();
        }
    });
}

function updateLastUpdatedTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const lastUpdated = document.getElementById("last-updated");
    if (lastUpdated) lastUpdated.textContent = `${hours}:${minutes}`;
}



   
