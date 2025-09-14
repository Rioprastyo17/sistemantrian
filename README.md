# Sistem Antrian

Sistem antrian sederhana yang dibangun dengan Python, Flask, dan antarmuka web. Sistem ini memungkinkan pengguna untuk mengambil nomor antrian untuk berbagai layanan, menampilkan status antrian saat ini di layar publik, dan menyediakan panel kontrol bagi operator untuk mengelola antrian.

## Fitur

  * **Antarmuka Kios**: Halaman web sederhana bagi pengguna untuk mengambil nomor antrian untuk layanan yang tersedia.
  * **Tampilan Publik**: Halaman web terpisah yang menampilkan nomor antrian yang sedang dipanggil, cocok untuk ditampilkan di monitor publik.
  * **Panel Kontrol Operator**: Aplikasi desktop yang memungkinkan operator untuk memanggil, mengulangi, melewati, atau menyelesaikan nomor antrian.
  * **Dukungan Text-to-Speech (TTS)**: Menggunakan Google Text-to-Speech (gTTS) untuk mengumumkan nomor antrian yang dipanggil melalui suara.
  * **Manajemen Basis Data**: Menggunakan SQLite untuk menyimpan dan mengelola data antrian, termasuk nomor antrian, jenis layanan, status, dan waktu.
  * **Pembuatan Tiket PDF**: Secara otomatis menghasilkan tiket antrian dalam format PDF yang dapat diunduh saat nomor antrian baru dibuat.

## Teknologi yang Digunakan

  * **Backend**:
      * Python
      * Flask
      * gTTS
      * pygame
  * **Frontend**:
      * HTML
      * CSS
      * JavaScript
  * **Basis Data**:
      * SQLite
  * **GUI Aplikasi**:
      * customtkinter

## Prasyarat

Sebelum Anda memulai, pastikan Anda telah menginstal Python 3 di sistem Anda.

## Penyiapan

1.  **Kloning Repositori**:

    ```bash
    git clone https://github.com/rioprastyo17/sistemantrian.git
    cd sistemantrian
    ```

2.  **Buat Lingkungan Virtual**:

    ```bash
    python -m venv venv
    ```

3.  **Aktifkan Lingkungan Virtual**:

      * **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
      * **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Instal Ketergantungan**:
    Arahkan ke direktori `server` dan instal paket yang diperlukan menggunakan `pip`:

    ```bash
    cd server
    pip install -r requirements.txt
    ```

## Menjalankan Aplikasi

1.  **Mulai Server**:
    Pastikan Anda berada di direktori `server` dan jalankan skrip `queue_server.py`:

    ```bash
    python queue_server.py
    ```

    Server sekarang akan berjalan di `http://localhost:5000`.

2.  **Akses Kios Klien**:
    Buka peramban web Anda dan navigasikan ke `http://localhost:5000/client/kiosk.html` untuk mengambil nomor antrian baru.

3.  **Buka Tampilan Publik**:
    Untuk melihat layar tampilan publik, buka `http://localhost:5000/display/index.html` di peramban lain.

4.  **Jalankan Panel Kontrol Operator**:
    Buka jendela terminal baru, aktifkan lingkungan virtual, arahkan ke direktori `server`, dan jalankan skrip `app.py`:

    ```bash
    python app.py
    ```

    Ini akan membuka aplikasi panel kontrol desktop tempat Anda dapat mengelola antrian.

## Struktur Proyek

```
sistemantrian/
├── client/
│   ├── kiosk.html
│   ├── script.js
│   └── style.css
├── display/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── server/
    ├── app.py
    ├── database.py
    ├── pdf_generator.py
    ├── queue_server.py
    ├── tts_engine.py
    ├── queue.db
    └── requirements.txt
```

### Deskripsi File

  * **`client/kiosk.html`**: Halaman web untuk pengguna mengambil nomor antrian.
  * **`display/index.html`**: Halaman web yang menampilkan nomor antrian saat ini yang sedang dipanggil.
  * **`server/app.py`**: Aplikasi panel kontrol desktop untuk operator.
  * **`server/database.py`**: Menangani semua operasi basis data, termasuk inisialisasi, penambahan, dan pembaruan antrian.
  * **`server/pdf_generator.py`**: Menghasilkan tiket antrian dalam format PDF.
  * **`server/queue_server.py`**: Aplikasi server Flask utama yang menangani permintaan API untuk manajemen antrian.
  * **`server/tts_engine.py`**: Mengelola fungsionalitas text-to-speech untuk mengumumkan nomor antrian.
  * **`server/queue.db`**: File basis data SQLite tempat semua data antrian disimpan.
  * **`server/requirements.txt`**: Daftar semua ketergantungan Python yang diperlukan untuk server.
