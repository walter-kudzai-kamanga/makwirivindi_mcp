// Simple Chart.js starter code
document.addEventListener('DOMContentLoaded', () => {

    // Create a sample chart if a canvas with id="chart1" exists
    const chartContainer = document.getElementById('chart1');
    if(chartContainer){
        const ctx = chartContainer.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Column 1', 'Column 2', 'Column 3', 'Column 4'],
                datasets: [{
                    label: 'Sample Dataset',
                    data: [12, 19, 3, 5],
                    backgroundColor: [
                        'rgba(0,123,255,0.7)',
                        'rgba(40,167,69,0.7)',
                        'rgba(255,193,7,0.7)',
                        'rgba(220,53,69,0.7)'
                    ],
                    borderColor: [
                        'rgba(0,123,255,1)',
                        'rgba(40,167,69,1)',
                        'rgba(255,193,7,1)',
                        'rgba(220,53,69,1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Sample Chart' }
                }
            }
        });
    }

});