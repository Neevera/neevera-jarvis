# 🎙️ Neevera: Personal PC Voice Assistant (Jarvis-Style)

Ever watched Iron Man and wished you had your own personal AI assistant like Jarvis? Meet **Neevera**!

Neevera is an intelligent voice assistant built with Python, specifically designed to control your Windows PC or laptop using voice commands and local LLM intelligence. From opening applications and browsing the web to managing core system settings, Neevera makes your digital life hands-free, smart, and much cooler.

---

## ✨ Fitur Utama (Key Features)

Neevera dilengkapi dengan berbagai kapabilitas:
- **Speech Recognition Offline & Online**: Menggunakan Vosk API untuk pengenalan suara offline yang cepat, akurat, dan hemat kuota, serta Google Speech Recognition untuk tugas online.
- **Local Brain (LLM)**: Terintegrasi dengan Ollama (`llama3.2:3b`) sebagai otak lokal untuk interaksi percakapan dan intepretasi perintah cerdas.
- **🛠️ App & Window Management**: Buka, tutup, atau minimize aplikasi seperti WhatsApp, Google Chrome, YouTube Music, dan File Manager dengan perintah suara.
- **🧹 Workspace Cleanup**: Menutup aplikasi yang terbuka secara terorganisir untuk membersihkan layar kerja Anda.
- **🌐 Automated Browsing**: Navigasi pencarian otomatis di YouTube, Google, atau TikTok tanpa perlu mengetik manual.
- **💻 System & Utility Controls**: Kontrol Wi-Fi, pengaturan hotspot, cek status baterai, cek waktu saat ini, atur volume audio, hingga ambil screenshot layar.
- **🛑 Safe Shutdown & Lock Screen**: Konfirmasi pintar sebelum mematikan atau mengunci laptop untuk menghindari kesalahan tindakan.
- **😴 Idle/Sleep Mode**: Perintahkan Neevera untuk tidur ("Go to sleep") dan bangunkan kembali cukup dengan mengatakan "Wake up".

---

## 🧠 Arsitektur Teknologi

- **Vosk & SpeechRecognition**: Sebagai indera pendengaran (telinga) offline dan online.
- **Ollama (`llama3.2:3b`)**: Otak lokal (LLM) untuk memahami konteks dan menjawab pertanyaan.
- **Pygame & pyttsx3**: Sebagai suara (output vokal) gabungan audio respon dan text-to-speech.
- **OS, Psutil, & PyAutoGUI**: Sebagai kontrol sistem Windows dan otomasi GUI.

---

## 📦 Prasyarat & Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/Neevera/neevera-jarvis.git
cd neevera-jarvis
```

### 2. Buat & Aktifkan Virtual Environment (Disarankan)
```bash
python -m venv venv
# Di Windows:
.\venv\Scripts\activate
```

### 3. Install Dependensi Python
```bash
pip install -r requirements.txt
```

---

## 📥 Setup Model Vosk (Speech Recognition)

> [!IMPORTANT]
> **Folder `model/` sengaja tidak disertakan di GitHub** karena ukurannya yang besar (>1.9 GB). Anda perlu mengunduh model speech recognition Vosk terlebih dahulu sebelum menjalankan asisten.

1. Kunjungi halaman resmi model Vosk: [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Unduh model bahasa Inggris universal yang Anda inginkan (misalnya: `vosk-model-en-us-0.22` atau `vosk-model-small-en-us-0.15`).
3. Ekstrak file zip tersebut.
4. Ubah nama folder hasil ekstraksi menjadi **`model`** dan letakkan langsung di root direktori project ini.

Struktur folder harus terlihat seperti berikut:
```text
neevera-jarvis/
├── model/                <-- Folder model diletakkan di sini
│   ├── am/
│   ├── conf/
│   ├── graph/
│   └── ivector/
├── voice/                <-- File respon audio
├── commands.txt
├── neevera.py
├── requirements.txt
└── README.md
```

---

## 🧠 Setup Ollama (LLM)

1. Pastikan Anda telah menginstal [Ollama](https://ollama.com/).
2. Unduh model `llama3.2:3b`:
   ```bash
   ollama run llama3.2:3b
   ```

---

## ▶️ Menjalankan Program

Jalankan script utama:
```bash
python neevera.py
```
atau menggunakan shortcut batch:
```bash
neevera.bat
```

Katakan wake word atau instruksi untuk mulai berinteraksi dengan Neevera!
