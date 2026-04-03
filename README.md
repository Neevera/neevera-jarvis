# 🎙️ Neevera: Personal PC Voice Assistant (Jarvis-Style)

Ever watched Iron Man and wished you had your own personal AI assistant like Jarvis? [cite_start]Meet **Neevera**! 

[cite_start]Neevera is an intelligent voice assistant built with Python, specifically designed to control your Windows PC or laptop using only voice commands[cite: 47, 52]. [cite_start]From opening applications and browsing the web to managing core system settings, Neevera makes your digital life hands-free and much cooler[cite: 46, 48].

---

## ✨ Key Features

[cite_start]Neevera is equipped with a wide range of skills to simplify your workflow: [cite: 46]

* [cite_start]**🛠️ App & Window Management**: Open, close, or minimize applications like WhatsApp, Chrome, YouTube Music, and File Manager with a simple phrase. [cite: 47, 50]
* **🧹 Workspace Cleanup ("Close Apps")**: Feeling overwhelmed by too many windows? [cite_start]Tell Neevera to close everything and instantly clear your desktop. 
* **🌐 Automated Browsing**: Skip the typing. [cite_start]Ask Neevera to "Search on YouTube" or "Search on Google," and it will automatically handle the search in your browser. 
* [cite_start]**💻 System & Utility Controls**: Toggle Wi-Fi, check battery levels, get the current time, take screenshots, or even lock your screen. [cite: 47, 48]
* [cite_start]**🛑 Safe Shutdown**: When asked to power down the PC, Neevera enters a standby confirmation mode to prevent accidental shutdowns. [cite: 48, 52]
* **😴 Idle/Sleep Mode**: When not in use, tell Neevera to "Go to sleep." [cite_start]It will stay quiet and only reactivate when it hears the "Wake up" command. 

---

## 🧠 Under the Hood

[cite_start]Neevera's intelligence is powered by several robust Python libraries: [cite: 53]

* **Vosk & SpeechRecognition**: Neevera's "ears." [cite_start]Vosk allows for offline command listening, while Google API is used for more complex online tasks. [cite: 53]
* **Pygame & System.Speech**: Neevera's "voice." [cite_start]A blend of custom MP3 recordings and Windows Text-to-Speech provides a natural and responsive interaction. [cite: 53]
* **OS, Psutil, & PyAutoGUI**: Neevera's "hands." [cite_start]These tools execute terminal scripts, monitor hardware status, and capture screen data. [cite: 53]

---

## 🚀 Installation & Setup

Ready to bring this voice assistant to your own machine? Follow these steps:

### 1. Install Dependencies
Ensure Python is installed on your laptop. [cite_start]Open your terminal in the project directory and install the required libraries: 
```bash
pip install -r requirements.txt
