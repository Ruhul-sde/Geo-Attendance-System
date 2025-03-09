
// Dashboard JavaScript

// Variables for location tracking
let map;
let userMarker;
let locationMarkers = [];
let userPosition = null;

// Initialize map
function initMap() {
    // Default center (will be updated with user location)
    const defaultPosition = { lat: 28.7041, lng: 77.1025 };
    
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: defaultPosition,
        mapTypeId: 'roadmap',
        streetViewControl: false
    });
    
    // Get locations from the select dropdown
    const locationSelect = document.getElementById('locationSelect');
    for(let i = 0; i < locationSelect.options.length; i++) {
        const option = locationSelect.options[i];
        const locationId = option.value;
        const locationName = option.text;
        const lat = parseFloat(option.getAttribute('data-lat'));
        const lng = parseFloat(option.getAttribute('data-lng'));
        
        // Add marker for each location
        const marker = new google.maps.Marker({
            position: { lat, lng },
            map: map,
            title: locationName
        });
        
        locationMarkers.push({
            id: locationId,
            marker: marker
        });
    }
    
    // Try to get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                userPosition = pos;
                
                // Center map on user location
                map.setCenter(pos);
                
                // Add marker for user
                userMarker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    title: 'Your Location',
                    icon: {
                        url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                    }
                });
            },
            () => {
                alert('Error: The Geolocation service failed.');
            }
        );
    } else {
        alert('Error: Your browser doesn\'t support geolocation.');
    }
}

// Show modal when mark attendance button is clicked
document.getElementById('markAttendanceBtn')?.addEventListener('click', function() {
    const modal = document.getElementById('locationModal');
    modal.style.display = 'block';
    
    // Refresh map
    setTimeout(() => {
        google.maps.event.trigger(map, 'resize');
        if (userMarker) {
            map.setCenter(userMarker.getPosition());
        }
    }, 100);
});

// Close modal when X is clicked
document.querySelector('.close')?.addEventListener('click', function() {
    document.getElementById('locationModal').style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('locationModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Mark attendance when confirm button is clicked
document.getElementById('confirmLocation')?.addEventListener('click', function() {
    if (!userPosition) {
        document.getElementById('attendanceMessage').innerHTML = 
            '<div class="error-message">Unable to get your location. Please enable location services.</div>';
        return;
    }
    
    const locationSelect = document.getElementById('locationSelect');
    const selectedLocationId = locationSelect.value;
    
    // Send attendance data to server
    fetch('/mark_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: userPosition.lat,
            longitude: userPosition.lng,
            location_id: selectedLocationId
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('attendanceMessage').innerHTML = 
                `<div class="success-message">${data.message}</div>`;
            
            // Reload page after 2 seconds
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            document.getElementById('attendanceMessage').innerHTML = 
                `<div class="error-message">${data.message}</div>`;
        }
    })
    .catch((error) => {
        document.getElementById('attendanceMessage').innerHTML = 
            `<div class="error-message">Error: ${error.message}</div>`;
    });
});
// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mark attendance functionality
    const markAttendanceBtn = document.getElementById('markAttendanceBtn');
    const locationModal = document.getElementById('locationModal');
    const closeModal = document.querySelector('.close');
    const confirmLocationBtn = document.getElementById('confirmLocation');
    const attendanceMessage = document.getElementById('attendanceMessage');
    
    if (markAttendanceBtn) {
        markAttendanceBtn.addEventListener('click', function() {
            locationModal.style.display = 'flex';
        });
    }
    
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            locationModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === locationModal) {
            locationModal.style.display = 'none';
        }
    });
    
    if (confirmLocationBtn) {
        confirmLocationBtn.addEventListener('click', function() {
            const locationSelect = document.getElementById('locationSelect');
            const locationId = locationSelect.value;
            
            // Get location coordinates
            markAttendance(locationId);
        });
    }
    
    function markAttendance(locationId) {
        attendanceMessage.style.display = 'none';
        
        fetch('/mark_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location_id: locationId
            })
        })
        .then(response => response.json())
        .then(data => {
            attendanceMessage.style.display = 'block';
            
            if (data.success) {
                attendanceMessage.textContent = data.message;
                attendanceMessage.className = 'success';
                
                // Reload after 2 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                attendanceMessage.textContent = data.message;
                attendanceMessage.className = 'error';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            attendanceMessage.style.display = 'block';
            attendanceMessage.textContent = 'An error occurred while marking attendance.';
            attendanceMessage.className = 'error';
        });
    }
});

// Google Maps initialization
function initMap() {
    // Check if the map container exists
    const mapElement = document.getElementById('map');
    if (!mapElement) return;
    
    // Default location (can be updated based on selected office)
    const defaultLocation = { lat: 28.7041, lng: 77.1025 };
    
    // Create map
    const map = new google.maps.Map(mapElement, {
        center: defaultLocation,
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: false,
        streetViewControl: false
    });
    
    // Create marker for current location
    const marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        title: 'Your Location',
        draggable: false
    });
    
    // Update map when location is selected
    const locationSelect = document.getElementById('locationSelect');
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            const selectedOption = locationSelect.options[locationSelect.selectedIndex];
            const lat = parseFloat(selectedOption.dataset.lat);
            const lng = parseFloat(selectedOption.dataset.lng);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                const newPosition = { lat, lng };
                map.setCenter(newPosition);
                marker.setPosition(newPosition);
            }
        });
        
        // Trigger change event to set initial location
        locationSelect.dispatchEvent(new Event('change'));
    }
}
