# Neevera - AI Voice Assistant (Jarvis)

Neevera adalah asisten suara desktop pribadi berbasis AI (Python) yang dapat mendengarkan perintah suara secara offline maupun online, mengontrol sistem Windows, dan mengintegrasikan model LLM lokal (Ollama - Llama 3.2).

---

## 🚀 Fitur Utama
- **Speech Recognition Offline**: Menggunakan Vosk API untuk pengenalan suara offline yang cepat, akurat, dan hemat kuota.
- **Local Brain (LLM)**: Integrasi dengan Ollama (`llama3.2:3b`) sebagai otak percakapan dan intepretasi perintah cerdas.
- **System Control & Automation**: 
  - Membuka/menutup aplikasi (Google Chrome, WhatsApp, Windows Settings, File Manager, dll).
  - Kontrol volume suara dan mute/unmute.
  - Kontrol Wi-Fi dan hotspot.
  - Navigasi browser (YouTube, Google, TikTok).
  - Mengambil screenshot layar.
  - Shutdown, lock screen, dan minimize windows.
- **Audio Feedback**: Menggunakan respon suara terintegrasi dan modul text-to-speech `pyttsx3`.

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

1. Pastikan Anda telah menginstal [Ollama](https://ollama.ai/).
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
atau menggunakan file batch:
```bash
neevera.bat
```

Katakan wake word atau instruksi untuk mulai berinteraksi dengan Neevera!
