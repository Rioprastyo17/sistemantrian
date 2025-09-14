const SERVER_URL = 'http://localhost:5000';

// Update timestamp
function updateTimestamp() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    document.getElementById('timestamp').textContent = 
        now.toLocaleDateString('id-ID', options);
}

// Fetch current queue data
function fetchCurrentQueue() {
    fetch(`${SERVER_URL}/api/display/current`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (data.current_queue) {
                    document.getElementById('currentQueue').textContent = data.current_queue;
                    document.getElementById('queueInfo').textContent = 
                        `Layanan ${data.service_type} - Panggilan ke ${data.call_count}`;
                    document.getElementById('callCount').textContent = data.call_count;
                } else {
                    document.getElementById('currentQueue').textContent = '-';
                    document.getElementById('queueInfo').textContent = 'Menunggu antrian baru';
                    document.getElementById('callCount').textContent = '0';
                }
                
                document.getElementById('waitingCount').textContent = data.waiting_count || 0;
            }
        })
        .catch(error => {
            console.error('Error fetching queue data:', error);
            // Show error state
            document.getElementById('currentQueue').textContent = 'ERROR';
            document.getElementById('queueInfo').textContent = 'Koneksi terputus';
        });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateTimestamp();
    fetchCurrentQueue();
    
    // Update every 3 seconds
    setInterval(updateTimestamp, 1000);
    setInterval(fetchCurrentQueue, 3000);
});