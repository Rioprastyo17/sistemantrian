import customtkinter as ctk
import requests
from tkinter import messagebox
from tts_engine import TTSEngine

# --- KONFIGURASI ---
# Pastikan alamat ini sama dengan alamat server Anda.
# Jika menjalankan di komputer yang berbeda, ganti 'localhost' dengan IP server.
BASE_URL = "http://localhost:5000/api"

# Tentukan satu layanan yang akan dikontrol oleh panel ini.
# NAMA INI HARUS SAMA PERSIS dengan yang ada di `queue_server.py`
SERVICE_TO_CONTROL = "PELAYANAN UMUM"

class ControlPanelApp:
    """Aplikasi desktop untuk operator mengontrol satu jalur antrian."""
    
    FONT_BOLD = ("CTkFont", 14, "bold")
    COLOR_PRIMARY = "#2980b9"
    COLOR_SUCCESS = "#27ae60"
    COLOR_WARNING = "#f39c12"
    COLOR_DANGER = "#e74c3c"
    COLOR_GOLD = "#f1c40f"

    def __init__(self, root):
        self.root = root
        self.tts = TTSEngine()
        self.current_queue = None
        
        self._configure_root_window()
        self._setup_ui()
        self.refresh_queue_list()

    def _configure_root_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.title(f"Panel Kontrol Antrian - {SERVICE_TO_CONTROL}")
        self.root.geometry("1000x600")
        self.root.minsize(900, 550)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_ui(self):
        # Konfigurasi grid utama dengan baris untuk status bar
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0) # Baris untuk status bar
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        # Frame Kiri: Panel Kontrol Utama
        left_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(left_frame, text=f"LOKET {SERVICE_TO_CONTROL}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 5))
        
        self.current_queue_label = ctk.CTkLabel(left_frame, text="-", font=ctk.CTkFont(size=100, weight="bold"), text_color=self.COLOR_GOLD)
        self.current_queue_label.pack(pady=20, expand=True)

        self.call_info_label = ctk.CTkLabel(left_frame, text="Tekan 'Panggil' untuk memulai", font=ctk.CTkFont(size=16))
        self.call_info_label.pack(pady=(0, 30))

        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        btn_config = {"font": self.FONT_BOLD, "height": 45, "corner_radius": 10, "width": 160}

        self.call_btn = ctk.CTkButton(button_frame, text="📞 PANGGIL", command=self.call_next_queue, fg_color=self.COLOR_SUCCESS, **btn_config)
        self.repeat_btn = ctk.CTkButton(button_frame, text="🔂 ULANGI", command=self.repeat_call, fg_color=self.COLOR_WARNING, **btn_config)
        self.skip_btn = ctk.CTkButton(button_frame, text="⏭ LEWATI", command=self.skip_queue, fg_color=self.COLOR_DANGER, **btn_config)
        self.complete_btn = ctk.CTkButton(button_frame, text="✅ SELESAI", command=self.complete_queue, fg_color=self.COLOR_PRIMARY, **btn_config)

        self.call_btn.grid(row=0, column=0, padx=10, pady=10)
        self.repeat_btn.grid(row=0, column=1, padx=10, pady=10)
        self.skip_btn.grid(row=1, column=0, padx=10, pady=10)
        self.complete_btn.grid(row=1, column=1, padx=10, pady=10)
        
        self._update_button_states(is_calling=False)

        # Frame Kanan: Daftar Antrian
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="Daftar Antrian Menunggu", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.queue_list_frame = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        self.queue_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Bilah Status di bagian bawah
        self.status_bar = ctk.CTkLabel(self.root, text="Siap", anchor="w", font=("CTkFont", 12))
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))

    def update_status(self, message, is_error=False):
        """Memperbarui teks dan warna pada bilah status."""
        self.status_bar.configure(text=message)
        if is_error:
            self.status_bar.configure(text_color="salmon")
        else:
            self.status_bar.configure(text_color="gray")

    def _api_request(self, method, endpoint, **kwargs):
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Server merespon dengan error {e.response.status_code}."
            self.update_status(error_msg, is_error=True)
            try:
                error_data = e.response.json()
                messagebox.showwarning("Peringatan Server", error_data.get('message', 'Aksi tidak diizinkan oleh server.'))
            except:
                messagebox.showerror("Error Server", error_msg)
            return None
        except requests.exceptions.RequestException as e:
            error_msg = "Gagal terhubung ke server. Periksa jaringan dan pastikan server berjalan."
            self.update_status(error_msg, is_error=True)
            messagebox.showerror("Error Jaringan", error_msg)
            return None

    def call_next_queue(self):
        endpoint = f'/queue/call?service={SERVICE_TO_CONTROL}'
        data = self._api_request('post', endpoint)
        if data and data.get('success'):
            self.current_queue = data['queue_number']
            self.current_queue_label.configure(text=self.current_queue)
            self.call_info_label.configure(text="Memanggil...")
            self._update_button_states(is_calling=True)
            
            try:
                self.tts.speak_queue(self.current_queue, SERVICE_TO_CONTROL)
                self.update_status(f"Antrian {self.current_queue} dipanggil.")
            except Exception as e:
                msg = "Panggilan berhasil, namun suara gagal diputar."
                self.update_status(msg, is_error=True)
                messagebox.showwarning("Peringatan Audio", f"{msg}\n\nDetail: {e}")
            
            self.refresh_queue_list()

    def repeat_call(self):
        if not self.current_queue:
            messagebox.showinfo("Info", "Tidak ada antrian aktif untuk diulangi.")
            return
        
        self.call_info_label.configure(text="Panggilan diulangi")
        try:
            self.tts.speak_queue(self.current_queue, SERVICE_TO_CONTROL)
            self.update_status(f"Panggilan untuk {self.current_queue} diulangi.")
        except Exception as e:
            msg = "Gagal memutar ulang suara."
            self.update_status(msg, is_error=True)
            messagebox.showwarning("Peringatan Audio", f"{msg}\n\nDetail: {e}")

    def skip_queue(self):
        if not self.current_queue: return
        if messagebox.askyesno("Konfirmasi", f"Anda yakin ingin melewati antrian {self.current_queue}?"):
            payload = {'queue_number': self.current_queue}
            data = self._api_request('post', '/queue/skip', json=payload)
            if data and data.get('success'):
                self.update_status(f"Antrian {self.current_queue} dilewati.")
                self.clear_current_queue()
                self.refresh_queue_list()

    def complete_queue(self):
        if not self.current_queue: return
        if messagebox.askyesno("Konfirmasi", f"Selesaikan layanan untuk {self.current_queue}?"):
            payload = {'queue_number': self.current_queue}
            data = self._api_request('post', '/queue/complete', json=payload)
            if data and data.get('success'):
                self.update_status(f"Antrian {self.current_queue} selesai.")
                self.clear_current_queue()
                self.refresh_queue_list()
                
    def clear_current_queue(self):
        self.current_queue = None
        self.current_queue_label.configure(text="-")
        self.call_info_label.configure(text="Tekan 'Panggil' untuk memulai")
        self._update_button_states(is_calling=False)

    def _update_button_states(self, is_calling: bool):
        call_state = "disabled" if is_calling else "normal"
        control_state = "normal" if is_calling else "disabled"
        
        self.call_btn.configure(state=call_state)
        self.repeat_btn.configure(state=control_state)
        self.skip_btn.configure(state=control_state)
        self.complete_btn.configure(state=control_state)

    def refresh_queue_list(self):
        """Mengambil data antrian terbaru dan memperbarui UI."""
        data = self._api_request('get', '/queues')
        
        for widget in self.queue_list_frame.winfo_children():
            widget.destroy()

        if data and data.get('success') and data.get('queues'):
            # PERBAIKAN: Mengakses data menggunakan nama kunci (dictionary)
            waiting_queues = [q for q in data['queues'] if q['service_type'] == SERVICE_TO_CONTROL and q['status'] == 'waiting']
            
            if not waiting_queues:
                ctk.CTkLabel(self.queue_list_frame, text="Tidak ada antrian.").pack(pady=20)
            else:
                for i, queue_data in enumerate(waiting_queues):
                    # PERBAIKAN: Mengakses nomor antrian menggunakan nama kunci
                    q_number = queue_data['queue_number']
                    item_frame = ctk.CTkFrame(self.queue_list_frame, fg_color=("gray80", "gray25"))
                    item_frame.pack(fill="x", padx=5, pady=5)
                    label_text = f"  {i+1}.   {q_number}"
                    ctk.CTkLabel(item_frame, text=label_text, font=("CTkFont", 16)).pack(anchor="w", padx=10, pady=10)
            self.update_status("Daftar antrian diperbarui.")
        else:
            ctk.CTkLabel(self.queue_list_frame, text="Tidak ada antrian.").pack(pady=20)
            if data: # Jika data tidak None, berarti request berhasil tapi tidak ada antrian
                self.update_status("Tidak ada antrian menunggu.")

        # Jadwalkan refresh berikutnya setelah 5 detik
        self.root.after(5000, self.refresh_queue_list)

    def _on_closing(self):
        self.root.destroy()
        
if __name__ == "__main__":
    root = ctk.CTk()
    app = ControlPanelApp(root)
    root.mainloop()

