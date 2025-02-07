fetch('/api/accidents')
    .then(response => response.json())
    .then(data => {
        const labels = data.map(row => row.Year);
        const accidents = data.map(row => row.Total_Accidents);

        new Chart(document.getElementById('accidentChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Accidents',
                    data: accidents,
                    borderColor: 'red',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }]
            }
        });
    });
