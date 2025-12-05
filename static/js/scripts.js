document.addEventListener('DOMContentLoaded', function () {

    // ==========================
    // SCORE BARS DYNAMIC FILL
    // ==========================
    const scoreBars = document.querySelectorAll('.score-fill');
    scoreBars.forEach(bar => {
        const value = bar.dataset.value;
        if (value) {
            bar.style.width = value + '%';
            bar.innerText = value + '%';
        }
    });

    // ==========================
    // PDF DOWNLOAD BUTTON
    // ==========================
    const pdfBtn = document.getElementById('download-pdf-btn');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', function () {
            // Use Flask route to serve the generated PDF
            const pdfUrl = pdfBtn.dataset.url;
            if (pdfUrl) {
                window.location.href = pdfUrl;
            }
        });
    }

    // ==========================
    // BASE64 CHARTS DISPLAY
    // ==========================
    // If Python sends charts as base64 strings, embed them directly
    const chartContainers = document.querySelectorAll('.chart-container img[data-base64]');
    chartContainers.forEach(img => {
        const base64 = img.dataset.base64;
        if (base64) {
            img.src = "data:image/png;base64," + base64;
        }
    });

    // ==========================
    // OPTIONAL: CHART.JS FOR DYNAMIC DATA
    // ==========================
    // Only enable if you switch to sending JSON datasets from Flask
    const chartCanvas = document.getElementById('materialChart');
    if (chartCanvas) {
        const labels = JSON.parse(chartCanvas.dataset.labels || "[]");
        const suitabilityData = JSON.parse(chartCanvas.dataset.suitability || "[]");
        const thermalData = JSON.parse(chartCanvas.dataset.thermal || "[]");
        const costData = JSON.parse(chartCanvas.dataset.cost || "[]");

        if (labels.length && suitabilityData.length) {
            const data = {
                labels: labels,
                datasets: [
                    {
                        label: 'Suitability',
                        data: suitabilityData,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)'
                    },
                    {
                        label: 'Thermal Performance',
                        data: thermalData,
                        backgroundColor: 'rgba(255, 159, 64, 0.7)'
                    },
                    {
                        label: 'Cost',
                        data: costData,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)'
                    }
                ]
            };

            const config = {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Multi-material Comparison' }
                    },
                    scales: { y: { beginAtZero: true } }
                },
            };

            new Chart(chartCanvas, config);
        }
    }

});
