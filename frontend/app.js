
const API_BASE_URL = '/api';
console.log("################")
console.log(API_BASE_URL)

// Initialisation de la carte
const map = L.map('map').setView([48.8566, 2.3522], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Couleurs pour les charts
const chartColors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
    '#7CFFB2', '#F465C1'
];

// Fonction pour récupérer les données de l'API
async function fetchData(endpoint) {
    try {
        const response = await fetch(`api${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return [];
    }
}

// Chart: Arbres par arrondissement
async function renderArrondissementChart() {
    const data = await fetchData('/trees/stats/arrondissements');
    
    const ctx = document.getElementById('arrondissementChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.arrondissement),
            datasets: [{
                label: "Nombre d'arbres",
                data: data.map(item => item.count),
                backgroundColor: chartColors,
                borderColor: chartColors.map(color => color.replace('0.2', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Distribution des arbres par arrondissement'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Chart: Espèces les plus communes
async function renderSpeciesChart() {
    const data = await fetchData('/trees/stats/species');
    
    const ctx = document.getElementById('speciesChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.espece || 'Non spécifié'),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: chartColors,
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Chart: Hauteur moyenne par espèce
async function renderHeightChart() {
    const data = await fetchData('/trees/stats/height');
    
    const ctx = document.getElementById('heightChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.espece),
            datasets: [
                {
                    label: 'Hauteur moyenne (m)',
                    data: data.map(item => item.avg_height),
                    backgroundColor: '#36A2EB',
                    borderColor: '#36A2EB',
                    borderWidth: 1
                },
                {
                    label: 'Hauteur maximale (m)',
                    data: data.map(item => item.max_height),
                    backgroundColor: '#FF6384',
                    borderColor: '#FF6384',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hauteur (mètres)'
                    }
                }
            }
        }
    });
}

// Chart: Arbres remarquables
async function renderRemarkableChart() {
    const data = await fetchData('/trees/stats/remarkable');
    
    const ctx = document.getElementById('remarkableChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.arrondissement),
            datasets: [
                {
                    label: 'Arbres remarquables',
                    data: data.map(item => item.remarkable_trees),
                    backgroundColor: '#4BC0C0',
                    borderColor: '#4BC0C0',
                    borderWidth: 1
                },
                {
                    label: 'Total des arbres',
                    data: data.map(item => item.total_trees),
                    backgroundColor: '#FFCE56',
                    borderColor: '#FFCE56',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Carte: Affichage des arbres
async function renderMap() {
    const data = await fetchData('/trees/geolocation');
    
    data.forEach(tree => {
        const popupContent = `
            <div class="tree-popup">
                <strong>${tree.nom || 'Arbre'}</strong><br>
                ${tree.espece ? `Espèce: ${tree.espece}<br>` : ''}
                ${tree.hauteur ? `Hauteur: ${tree.hauteur}m<br>` : ''}
                ${tree.remarquable ? '<span style="color: red;">⭐ Arbre remarquable</span>' : ''}
            </div>
        `;
        
        const markerColor = tree.remarquable ? 'red' : 'green';
        
        L.circleMarker([tree.latitude, tree.longitude], {
            color: markerColor,
            fillColor: markerColor,
            fillOpacity: 0.5,
            radius: 5
        })
        .bindPopup(popupContent)
        .addTo(map);
    });
}

// Initialisation de toutes les visualisations
async function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    try {
        await Promise.all([
            renderArrondissementChart(),
            renderSpeciesChart(),
            renderHeightChart(),
            renderRemarkableChart(),
            renderMap()
        ]);
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

// Démarrer l'application quand la page est chargée
document.addEventListener('DOMContentLoaded', initializeDashboard);