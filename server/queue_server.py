from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import init_db, get_next_queue_number, add_queue, get_queues_by_status, update_queue_status
import os

# --- KONFIGURASI ---
# Ini adalah satu-satunya tempat Anda perlu mendefinisikan layanan.
AVAILABLE_SERVICES = ["PELAYANAN UMUM"]

# Membuat pemetaan prefix dari nama layanan
SERVICE_PREFIX_MAP = {
    name: ''.join([word[0] for word in name.split()]).upper()
    for name in AVAILABLE_SERVICES
}

app = Flask(__name__, static_folder='client')
CORS(app)

# Panggil init_db() sekali saat server dimulai
init_db()

# --- API Endpoints ---

@app.route('/client/<path:filename>')
def serve_client_files(filename):
    """Menyajikan file statis untuk kios klien (kiosk.html)."""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/services', methods=['GET'])
def get_services():
    """Endpoint untuk klien mengambil daftar layanan yang tersedia."""
    return jsonify({"success": True, "services": AVAILABLE_SERVICES})

@app.route('/api/queue/new', methods=['POST'])
def create_new_queue():
    """Endpoint untuk membuat nomor antrian baru."""
    try:
        data = request.get_json()
        service_type = data.get('service_type')

        if not service_type or service_type not in AVAILABLE_SERVICES:
            return jsonify({"success": False, "message": "Jenis layanan tidak valid"}), 400

        # 1. Dapatkan HANYA ANGKA dari database
        next_number = get_next_queue_number(service_type)
        
        # 2. Server bertanggung jawab memformat string nomor antrian
        prefix = SERVICE_PREFIX_MAP.get(service_type, "Q")
        queue_number_str = f"{prefix}-{next_number:03d}"
        
        # 3. Tambahkan nomor antrian yang sudah diformat ke database
        add_queue(queue_number_str, service_type)
        
        return jsonify({"success": True, "queue_number": queue_number_str})
    except Exception as e:
        # Log error ke terminal untuk debugging
        print(f"ERROR in create_new_queue: {e}")
        return jsonify({"success": False, "message": f"Gagal membuat antrian."}), 500

@app.route('/api/queue/call', methods=['POST'])
def call_next_queue():
    """Endpoint untuk memanggil antrian berikutnya berdasarkan layanan."""
    try:
        service_type = request.args.get('service')
        if not service_type or service_type not in AVAILABLE_SERVICES:
            return jsonify({"success": False, "message": "Jenis layanan tidak valid"}), 400

        waiting_queues = get_queues_by_status('waiting', service_type)
        if not waiting_queues:
            return jsonify({"success": False, "message": f"Tidak ada antrian menunggu untuk {service_type}"}), 404
            
        next_queue = waiting_queues[0]
        queue_number = next_queue['queue_number']
        
        update_queue_status(queue_number, 'called')
        return jsonify({"success": True, "queue_number": queue_number})
    except Exception as e:
        print(f"ERROR in call_next_queue: {e}")
        return jsonify({"success": False, "message": "Terjadi kesalahan internal saat memanggil antrian."}), 500

@app.route('/api/queue/complete', methods=['POST'])
def complete_queue():
    try:
        data = request.get_json()
        queue_number = data.get('queue_number')
        if not queue_number:
            return jsonify({"success": False, "message": "Nomor antrian dibutuhkan"}), 400
        
        update_queue_status(queue_number, 'completed')
        return jsonify({"success": True, "message": f"Antrian {queue_number} selesai."})
    except Exception as e:
        print(f"ERROR in complete_queue: {e}")
        return jsonify({"success": False, "message": "Terjadi kesalahan internal saat menyelesaikan antrian."}), 500


@app.route('/api/queue/skip', methods=['POST'])
def skip_queue():
    try:
        data = request.get_json()
        queue_number = data.get('queue_number')
        if not queue_number:
            return jsonify({"success": False, "message": "Nomor antrian dibutuhkan"}), 400

        update_queue_status(queue_number, 'skipped')
        return jsonify({"success": True, "message": f"Antrian {queue_number} dilewati."})
    except Exception as e:
        print(f"ERROR in skip_queue: {e}")
        return jsonify({"success": False, "message": "Terjadi kesalahan internal saat melewati antrian."}), 500

@app.route('/api/queues', methods=['GET'])
def get_all_queues():
    """Endpoint untuk mendapatkan semua data antrian (untuk panel kontrol)."""
    try:
        db_rows = get_queues_by_status(None)
        # Konversi objek Row menjadi dictionary agar bisa di-serialize ke JSON
        all_queues = [dict(row) for row in db_rows] 
        return jsonify({"success": True, "queues": all_queues})
    except Exception as e:
        print(f"ERROR in get_all_queues: {e}")
        return jsonify({"success": False, "message": "Terjadi kesalahan internal saat mengambil data antrian."}), 500

@app.route('/api/display/current', methods=['GET'])
def get_current_for_display():
    """Endpoint untuk monitor publik, menampilkan antrian yang sedang dipanggil."""
    try:
        db_rows = get_queues_by_status('called')
        # Konversi objek Row menjadi dictionary
        called_queues = [dict(row) for row in db_rows]
        return jsonify({"success": True, "called_queues": called_queues})
    except Exception as e:
        print(f"ERROR in get_current_for_display: {e}")
        return jsonify({"success": False, "message": "Terjadi kesalahan internal saat mengambil data display."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
