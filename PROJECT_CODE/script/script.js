// Fonction pour récupérer les valeurs des capteurs via HTTP GET
function getSensorValues() {
    fetch('/temperature') // Requête pour récupérer la valeur de température
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature').innerHTML = `
                <h2>${data.name}</h2>
                <p>Description: ${data.description}</p>
                <p>Type: ${data.type}</p>
                <p>Unité: ${data.unit}</p>
                <p>Valeur: ${data.value}</p>
                <p>Fréquence: ${data.frequency}</p>
                <p>Timestamp: ${data.timestamp}</p>
            `;
        });

    fetch('/light') // Requête pour récupérer la valeur de lumière
        .then(response => response.json())
        .then(data => {
            document.getElementById('light').innerHTML = `
                <h2>${data.name}</h2>
                <p>Description: ${data.description}</p>
                <p>Type: ${data.type}</p>
                <p>Unité: ${data.unit}</p>
                <p>Valeur: ${data.value}</p>
                <p>Fréquence: ${data.frequency}</p>
                <p>Timestamp: ${data.timestamp}</p>
            `;
        });
    
}

// Actualiser les valeurs des capteurs toutes les 5 secondes
setInterval(getSensorValues, 5000);

// Appel initial pour obtenir les valeurs des capteurs dès le chargement de la page
getSensorValues();