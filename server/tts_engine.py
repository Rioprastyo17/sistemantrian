from gtts import gTTS
import pygame
import threading
import io
import time

class TTSEngine:
    def __init__(self):
        """Inisialisasi pygame mixer untuk pemutaran audio."""
        try:
            pygame.mixer.init()
            print("TTS Engine initialized successfully.")
        except pygame.error as e:
            print(f"!!! TTS WARNING: Could not initialize pygame.mixer. No audio will be played. Error: {e}")
            # Atur flag agar kita tahu mixer tidak berfungsi
            self._mixer_initialized = False
        else:
            self._mixer_initialized = True

    def _speak_message_thread(self, message):
        """Fungsi yang dijalankan di thread terpisah untuk menghasilkan dan memutar suara."""
        if not self._mixer_initialized:
            print(f"TTS SKIPPED (Mixer not initialized): {message}")
            return

        try:
            # Hentikan musik yang sedang berjalan untuk mencegah tumpang tindih
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload() # Pastikan sumber daya dilepaskan
                time.sleep(0.1) # Beri jeda singkat

            print(f"TTS Generating: '{message}'")
            # Buat objek gTTS dengan bahasa Indonesia
            tts = gTTS(text=message, lang='id', slow=False)
            
            # Simpan audio ke buffer memori, bukan file fisik
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            
            # Muat dan putar audio dari buffer memori
            pygame.mixer.music.load(mp3_fp)
            pygame.mixer.music.play()
            
            print("TTS Playing...")
            # Tunggu hingga pemutaran selesai
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("TTS Finished.")

        except Exception as e:
            # Tangkap semua jenis error (koneksi internet, dll)
            print(f"!!! TTS ERROR: Failed to generate or play audio. Message: '{message}'. Error: {e}")

    def speak_queue(self, queue_number, service_type):
        """Menyuarakan nomor antrian untuk layanan spesifik."""
        # Format angka menjadi "satu, dua, tiga" agar lebih jelas
        number_spoken = " ".join(list(queue_number.replace("-", " ")))
        
        # Format pesan yang akan diucapkan
        message = f"Nomor antrian, {number_spoken}, silakan menuju loket, {service_type}"
        
        # Jalankan di thread terpisah agar tidak memblokir antarmuka utama
        thread = threading.Thread(target=self._speak_message_thread, args=(message,))
        thread.daemon = True
        thread.start()

# --- Blok untuk Pengujian Langsung ---
# Anda bisa menjalankan file ini secara langsung untuk menguji fungsi TTS
if __name__ == '__main__':
    print("--- Melakukan Tes TTS Engine ---")
    engine = TTSEngine()
    
    if engine._mixer_initialized:
        print("\nTes 1: Memanggil nomor antrian PU-001...")
        engine.speak_queue("PU-001", "Pelayanan Umum")
        time.sleep(8) # Tunggu suara selesai

        print("\nTes 2: Memanggil nomor antrian PU-123...")
        engine.speak_queue("PU-123", "Pelayanan Umum")
        time.sleep(8)

        print("\n--- Tes Selesai ---")
    else:
        print("\n--- Tes Dibatalkan: Pygame mixer gagal diinisialisasi. Periksa perangkat audio Anda. ---")

