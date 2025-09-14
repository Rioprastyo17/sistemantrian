import sqlite3
import threading
from datetime import datetime

# Menggunakan Thread-Local storage untuk koneksi database yang aman
local_storage = threading.local()

def get_db_conn():
    """Membuka koneksi database baru per-thread dengan row_factory."""
    if not hasattr(local_storage, 'conn'):
        # Menghubungkan ke database dan memastikan thread-safety
        local_storage.conn = sqlite3.connect('queue.db', check_same_thread=False)
        # Mengatur row_factory agar hasil query bisa diakses seperti dictionary
        local_storage.conn.row_factory = sqlite3.Row
    return local_storage.conn

def init_db():
    """Inisialisasi tabel database."""
    conn = get_db_conn()
    cursor = conn.cursor()
    # Tabel untuk menyimpan nomor terakhir per layanan per hari
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_counters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT NOT NULL,
            last_number INTEGER NOT NULL,
            date TEXT NOT NULL,
            UNIQUE(service_type, date)
        )
    ''')
    # Tabel antrian utama
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queue_number TEXT UNIQUE NOT NULL,
            service_type TEXT NOT NULL,
            status TEXT DEFAULT 'waiting',
            created_at TIMESTAMP NOT NULL,
            called_at TIMESTAMP,
            completed_at TIMESTAMP,
            priority INTEGER DEFAULT 3,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()

def get_next_queue_number(service_type):
    """
    Mendapatkan nomor urut berikutnya untuk layanan tertentu pada hari ini.
    HANYA mengembalikan angka (integer), bukan string yang diformat.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    with conn: # Transaksi otomatis untuk mencegah race condition
        cursor.execute(
            "SELECT last_number FROM service_counters WHERE service_type = ? AND date = ?",
            (service_type, today_str)
        )
        row = cursor.fetchone()

        if row:
            new_number = row['last_number'] + 1
            cursor.execute(
                "UPDATE service_counters SET last_number = ? WHERE service_type = ? AND date = ?",
                (new_number, service_type, today_str)
            )
        else:
            new_number = 1
            cursor.execute(
                "INSERT INTO service_counters (service_type, last_number, date) VALUES (?, ?, ?)",
                (service_type, new_number, today_str)
            )
        return new_number

def add_queue(queue_number, service_type, priority=3):
    """Menambahkan antrian baru ke database."""
    conn = get_db_conn()
    with conn:
        conn.execute(
            """
            INSERT INTO queues (queue_number, service_type, status, created_at, priority, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                queue_number,
                service_type,
                'waiting',
                datetime.now(),
                priority,
                datetime.now().strftime('%Y-%m-%d')
            )
        )

def update_queue_status(queue_number, new_status):
    """
    Memperbarui status antrian. Versi ini lebih sederhana dan andal.
    """
    conn = get_db_conn()
    
    query = f"UPDATE queues SET status = ?"
    params = [new_status]

    # Menambahkan kolom timestamp yang sesuai secara dinamis
    if new_status == 'called':
        query += ", called_at = ?"
        params.append(datetime.now())
    elif new_status == 'completed':
        query += ", completed_at = ?"
        params.append(datetime.now())

    query += " WHERE queue_number = ?"
    params.append(queue_number)
    
    with conn:
        conn.execute(query, tuple(params))

def get_queues_by_status(status=None, service_type=None):
    """Mendapatkan daftar antrian berdasarkan status dan/atau layanan."""
    conn = get_db_conn()
    
    query = "SELECT * FROM queues"
    conditions = []
    params = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if service_type:
        conditions.append("service_type = ?")
        params.append(service_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY created_at ASC"
    
    cursor = conn.execute(query, tuple(params))
    return cursor.fetchall()

def get_stats_counts():
    """Mendapatkan jumlah antrian berdasarkan status."""
    conn = get_db_conn()
    query = """
        SELECT
            (SELECT COUNT(*) FROM queues WHERE status = 'waiting') as waiting,
            (SELECT COUNT(*) FROM queues WHERE status = 'completed' AND date = date('now', 'localtime')) as completed_today,
            (SELECT COUNT(*) FROM queues WHERE status = 'skipped' AND date = date('now', 'localtime')) as skipped_today
    """
    cursor = conn.execute(query)
    return cursor.fetchone()

