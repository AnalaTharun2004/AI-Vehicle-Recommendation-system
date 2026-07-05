// Vehicle Recommendation System - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Vehicle Recommendation System loaded');
    
    // Add event listeners and functionality here
    initializeEventListeners();
});

function initializeEventListeners() {
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Classification tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    const activeTabKey = 'activeVehicleClassificationTab';

    function activateTab(tabName) {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabPanels.forEach(panel => panel.classList.remove('active'));

        const activeButton = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
        const activePanel = document.querySelector(`.tab-panel[data-tab="${tabName}"]`);

        if (activeButton) activeButton.classList.add('active');
        if (activePanel) activePanel.classList.add('active');
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            activateTab(tabName);
            localStorage.setItem(activeTabKey, tabName);
        });
    });

    const savedTab = localStorage.getItem(activeTabKey) || 'vehicle_type';
    activateTab(savedTab);
}

function handleFormSubmit(event) {
    // Handle form submission
    console.log('Form submitted');
}

// Fetch recommendations from server
async function fetchRecommendations(preferences) {
    try {
        const response = await fetch('/result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(preferences)
        });
        
        if (response.ok) {
            const data = await response.json();
            displayRecommendations(data);
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
    }
}

function displayRecommendations(recommendations) {
    // Display recommendations on the page
    const resultsContainer = document.querySelector('.results');
    
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    recommendations.forEach(vehicle => {
        const card = createVehicleCard(vehicle);
        resultsContainer.appendChild(card);
    });
}

function createVehicleCard(vehicle) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
        <h3>${vehicle.name}</h3>
        <p><strong>Price:</strong> ${vehicle.price}</p>
        <p><strong>Rating:</strong> ${vehicle.rating}</p>
        <p><strong>Features:</strong> ${vehicle.features}</p>
    `;
    return card;
}
