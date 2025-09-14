const SERVER_URL = 'http://localhost:5000';

// Generate barcode when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateBarcode();
});

function updateBarcode() {
    const serviceType = document.getElementById('serviceType').value;
    
    // Generate QR Code data for SERVICE request
    const barcodeData = `GENERATE_QUEUE:${serviceType}`;
    
    // Create QR Code image URL using online service
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(barcodeData)}&size=250x250`;
    
    document.getElementById('barcodeImage').src = qrUrl;
    
    // Add click handler for testing
    document.getElementById('barcodeImage').onclick = function() {
        generateQueueFromScan(serviceType);
    };
}

function generateQueueFromScan(serviceType) {
    // Simulate barcode scanning by directly calling the API
    fetch(`${SERVER_URL}/api/queue/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ service_type: serviceType })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Queue generated:', data);
            
            // Auto download PDF
            setTimeout(() => {
                try {
                    // Create download link
                    const link = document.createElement('a');
                    link.href = data.pdf_url;
                    link.download = `ticket_${data.queue_number}.pdf`;
                    link.target = '_blank';
                    
                    // Append to body, click, and remove
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    alert(`Antrian ${data.queue_number} berhasil dibuat! PDF sedang terdownload.`);
                } catch (downloadError) {
                    console.error('Download error:', downloadError);
                    // Fallback: open in new tab
                    window.open(data.pdf_url, '_blank');
                    alert(`Antrian ${data.queue_number} berhasil dibuat! PDF akan terbuka di tab baru.`);
                }
            }, 1000);
        } else {
            alert('Gagal: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan saat menghubungi server: ' + error.message);
    });
}

// Simulate barcode scanning for testing
function simulateBarcodeScan() {
    const serviceType = document.getElementById('serviceType').value;
    generateQueueFromScan(serviceType);
}