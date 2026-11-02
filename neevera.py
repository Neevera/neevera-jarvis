import os
import webbrowser
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame 
import random
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
import pyautogui
import datetime
import psutil
from pycaw.pycaw import AudioUtilities
import ctypes
import pyttsx3
import ollama
import re

engine = pyttsx3.init()
engine.setProperty('rate', 165)
engine.setProperty('volume', 1.0)

def tanya_llm(user_input):
    print("\n[Red Neevera is Thinking...]")
    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {
                    'role': 'system',
                    'content': 'Your name is Red Neevera (or simply Red). You are an AI created by Neev (Hanif). If the user EXPLICITLY asks you to perform a system action (like opening an app, search, Wi-Fi, battery, time), output ONLY a tag like: [CMD: open whatsapp], [CMD: close chrome], [CMD: search on youtube], [CMD: search on google], [CMD: check battery]. For search, DO NOT guess the keyword, just use [CMD: search on youtube]. Do NOT output any [CMD] tags during casual questions or chats! Refuse shutdown/lock politely. Keep verbal answers under 2 sentences.'
                },
                {
                    'role': 'user',
                    'content': user_input
                }
            ]
        )
        jawaban = response['message']['content']
        return jawaban
    except Exception as e:
        print(f"[LLM Error: {e}]")
        return "Sorry, I am having trouble connecting to my local brain right now."

# SETUP VOSK (TELINGA BARU)

q = queue.Queue()

# GOOGLE SPEECH RECOGNIZER
telinga = sr.Recognizer()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = Model("model")  

# KAMUS GRAMMAR KHUSUS MODE NEEVERA (Cepat & Akurat Sesuai Kata Kunci Bawaan)
grammar_list = [   
    "okay", "alright", "aight", "so", "yes", "no", "sure", "cancel",
    "are you good", "how are you", "go to sleep", "open", "minimize",
    "open whatsapp", "open youtube", "open settings", "open whats app", "open instagram",
    "open music", "open youtube music", "open file manager", "explorer", "close",
    "close whatsapp", "close settings", "close file manager", "close chrome", "close google chrome",
    "search on", "search on youtube", "search on tiktok", "search on tik tok",
    "hide yourself", "minimize yourself", "minimize apps", "minimize everything",
    "show yourself", "come back", "close apps", "who are you", "hello", "help", "exit", "stop",
    "hey neevera", "neevera", "neev era", "neev", "era", "what can you do", "standby", "wake up",
    "who built you", "who is your bos", "who created you", "who made you",
    "turn on wifi", "hotspot", "turn off wifi", "screenshot", "check battery", "battery status",
    "what time is it", "capture screen", "system wake up", "kill chrome", "kill google chrome",
    "lock my computer", "lock screen", "shut down the computer", "turn off the computer",
    "yes turn off the computer", "sure turn off the computer", "yes shutdown the computer",
    "sure shutdown the computer", "what day is it", "what day is today",
    "red", "read", "rat", "rad", "rect", "llm", "jarvis", "switch to red", "switch to rat", "activate red", "red neevera",
    "blue", "switch to blue", "activate blue", "blue neevera",
    "neev", "hanif", "creator", "boss", "who created you", "who made you", "who built you", "who is your boss", "who is your creator",
    "online mode", "offline mode", "switch to online", "switch to offline", "use google voice", "use offline voice"
]

rec_grammar = KaldiRecognizer(model, 16000, json.dumps(grammar_list))
rec_free = KaldiRecognizer(model, 16000) # Tanpa pembatasan kamus untuk LLM

def dengar_vosk():
    with q.mutex:
        q.queue.clear()
    
    # Pilih recognizer sesuai mode aktif
    active_rec = rec_grammar if active_mode == "neevera" else rec_free
    
    # Mode Red (LLM) butuh jeda hening lebih panjang (misal ~1 detik) agar user bisa berfikir/berbicara kalimat panjang
    # Mode Blue (Rule-based) tetap cepat responsif (~0.4 detik) untuk perintah singkat
    ambang_hening = 4 if active_mode == "neevera" else 9
        
    with sd.RawInputStream(samplerate=16000, blocksize=1500,
                           dtype='int16', channels=1, callback=callback):
        print("\nListening...")
        last_partial = ""
        silence_count = 0
        
        while True:
            data = q.get()
            if active_rec.AcceptWaveform(data):
                hasil = json.loads(active_rec.Result())
                teks_hasil = hasil.get("text", "").strip()
                if teks_hasil != "":
                    return teks_hasil
            else:
                partial_json = json.loads(active_rec.PartialResult())
                partial_text = partial_json.get("partial", "").strip()
                
                if partial_text != "":
                    if partial_text == last_partial:
                        silence_count += 1
                        if silence_count >= ambang_hening:
                            res = json.loads(active_rec.FinalResult())
                            final_text = res.get("text", "").strip()
                            teks_final = final_text if final_text != "" else partial_text
                            
                            # Abaikan suara desis/kebisingan mikrofon (noise) seperti kata tunggal "the", "a", "uh"
                            if teks_final.lower() in ["the", "a", "an", "uh", "um", "huh", "the the"]:
                                silence_count = 0
                                last_partial = ""
                                continue
                            return teks_final
                    else:
                        last_partial = partial_text
                        silence_count = 0

# FUNGSI MUTE APLIKASI LAIN

def atur_suara_lain(bisu):
    # Ambil daftar semua aplikasi yang lagi ngeluarin suara di Windows
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            volume = session.SimpleAudioVolume
            # Kalo aplikasi yang bunyi itu bukan program kodingan kita (python.exe)
            if session.Process and session.Process.name() != "python.exe":
                if bisu == True:
                    volume.SetMute(1, None) 
                else:
                    volume.SetMute(0, None) 
        except:
            pass

# LISTENING ENGINE MODE UNTUK RED NEEVERA: "offline" (Vosk) atau "online" (Google SpeechRecognition)
stt_mode = "offline"

def dengar_google():
    with sr.Microphone() as sumber:
        print("\nListening (Online Mode)...")
        telinga.pause_threshold = 1.0
        telinga.adjust_for_ambient_noise(sumber, duration=0.3)
        try:
            audio = telinga.listen(sumber, timeout=10)
            teks = telinga.recognize_google(audio, language="en-US")
            return teks
        except sr.WaitTimeoutError:
            return ""
        except Exception:
            return ""

def ngomong_langsung(teks):
    print("Assistant: " + teks)
    try:
        atur_suara_lain(bisu=True)
        # Windows SAPI / System.Speech (Offline & Sangat Cepat)
        teks_safe = teks.replace("'", "").replace('"', '').replace("\n", " ")
        mantra = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{teks_safe}\')"'
        os.system(mantra)
        atur_suara_lain(bisu=False)
    except Exception as e:
        atur_suara_lain(bisu=False)
        print(f"[System TTS Error: {e}]")

# SUARA PYGAME
try:
    pygame.mixer.init()
except Exception as e:
    print(f"[Pygame Mixer Init Warning: {e}]")

def play_recording(screen_text, mp3_file_name):
    print("Assistant: " + screen_text)
    
    try:
        atur_suara_lain(bisu=True)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(mp3_file_name)
        pygame.mixer.music.set_volume(1.0) 
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        atur_suara_lain(bisu=False)
    except Exception as e:
        atur_suara_lain(bisu=False)
        # Jika file mp3 gagal diputar, gunakan TTS sebagai fallback!
        ngomong_langsung(screen_text)

# STARTUP VOICE

play_recording("Hello! Neevera here.", "voice/Hello, Neevera here!.mp3")

print("\n[System: Voice assistant is starting, say 'Help' to see the commands]")

# PROGRAM UTAMA

idle_mode = False
konfirmasi_shutdown = False
active_mode = "neevera" # Pilihan mode: "neevera" (Rule-Based Only) atau "red" (LLM Only)

print("\n[System Ready: Default mode is 'Blue Neevera'. Say 'Red' to switch to Red Neevera Mode!]")

while True:
    try:
        # Pada mode Red, gunakan engine pendengar sesuai stt_mode (online: Google SR, offline: Vosk)
        if active_mode == "red" and stt_mode == "online":
            teks = dengar_google()
        else:
            teks = dengar_vosk()
            
        perintah = teks.lower().strip()
        print("You said:", perintah)

        if perintah == "":
            continue

    except:
        print("Error listening...")
        continue

    # SWITCH MODE CONTROL (Pengecekan kata kunci fleksibel dengan kemiripan fonetik)
    kata_switch_red = ["red", "read", "rat", "rad", "rect", "llm", "jarvis", "switch to red", "switch to rat", "activate red", "red neevera"]
    kata_switch_blue = ["blue", "neevera", "never", "rule", "rule based", "switch to blue", "switch to neevera", "activate blue", "blue neevera"]

    if any(k in perintah for k in kata_switch_red) and active_mode != "red":
        active_mode = "red"
        ngomong_langsung("Red Neevera mode activated. How can I help you?")
        continue
    elif any(k in perintah for k in kata_switch_blue) and active_mode != "neevera":
        active_mode = "neevera"
        ngomong_langsung("Switched back to Blue Neevera.")
        continue
    
    # JIKA MODE 'RED' AKTIF -> HANYA PROSES DENGAN LLM (TANPA RULE-BASED)
    if active_mode == "red":
        if "go to sleep" in perintah or "standby" in perintah or "sleep" in perintah:
            idle_mode = True
            play_recording("Alright, I'm going to sleep.", "voice/Alright, I'm going to sleep, Just say wake up if you need me.mp3")
            continue
        elif "exit" in perintah or "stop" in perintah:
            ngomong_langsung("Goodbye Neev! Deactivating Red Neevera.")
            break # Keluar langsung dari program/terminal
        
        # Switch Listening Speech Recognition Mode (Online Google STT vs Offline Vosk STT)
        if "switch to online" in perintah or "online mode" in perintah or "use google speech" in perintah:
            stt_mode = "online"
            ngomong_langsung("Switched Red Neevera to online Google speech recognition mode.")
            continue
        elif "switch to offline" in perintah or "offline mode" in perintah or "use vosk" in perintah or "use offline speech" in perintah:
            stt_mode = "offline"
            ngomong_langsung("Switched Red Neevera to offline Vosk speech recognition mode.")
            continue

        # Deteksi pencarian berita/kejadian terkini di Indonesia untuk membuka portal berita nasional utama
        if "what is happening in my country" in perintah or "what is happening" in perintah or "indonesia news" in perintah or "national news" in perintah:
            webbrowser.open("https://news.detik.com/")
            webbrowser.open("https://www.kompas.com/")
            webbrowser.open("https://www.cnnindonesia.com/")
            webbrowser.open("https://www.tempo.co/")
            ngomong_langsung("Here is some information about what is currently happening based on the latest headlines from the top national news sites I've opened for you Neev. Please take a look at the windows on your screen to stay updated.")
            continue

        # Kirim ucapan pengguna langsung ke LLM
        jawaban = tanya_llm(perintah)
        
        # Ekstrak COMMAND TAG dari Red Neevera LLM
        cmd_match = re.search(r'\[CMD:\s*(.*?)\]', jawaban, re.IGNORECASE)
        if cmd_match:
            hasil_cmd = cmd_match.group(1).strip()
            
            # Timpa variabel perintah lalu biarkan jatuh (fall-through) ke logika rule-based di bawah
            perintah = hasil_cmd.lower()
            print(f"[Red Neevera intent matched System Action: {perintah}]")
        else:
            # Jika bukan perintah sistem, baru bicarakan sebagai jawaban natural LLM
            ngomong_langsung(jawaban)
            continue

    # -------------------------------------------------------------
    # JIKA MODE 'NEEVERA' AKTIF -> HANYA PROSES RULE-BASED SAJA
    # -------------------------------------------------------------
    
    # LOGIKA MODE IDLE (TIDUR)
    
    if idle_mode == True:
        if "wake up" in perintah:
            idle_mode = False 
            
            # Neevera ngecek buat matiin laptop bukan 
            if konfirmasi_shutdown == True:
                play_recording("I am awake. Are you sure you want to shut down the computer?\n[System: say 'Yes turn off the computer' or 'No/Cancel']\n", "voice/I am awake. Are you sure you want to shut down the computer.mp3")
                jawaban = dengar_vosk().lower()
                print("You answered:", jawaban)
                
                if "yes turn off the computer" in jawaban or "sure turn off the computer" in jawaban or "yes shutdown the computer" in jawaban or "sure shutdown the computer" in jawaban:
                    play_recording("Shutting down the computer. Goodbye!", "voice/Shutting down the computer. Goodbye.mp3")
                    os.system("shutdown /s /t 5") 
                    break 
                    
                elif "no" in jawaban or "cancel" in jawaban:
                    # Kalo batal, matiin saklar bahayanya
                    konfirmasi_shutdown = False 
                    play_recording("Shutdown canceled. I am still here and ready for commands.", "voice/Shutdown canceled. I am still here and ready for commands.mp3")
                
                else:
                    play_recording("I didn't catch a clear 'Yes' or 'No', canceling the shutdown.", "voice/I didn't catch a clear 'Yes' or 'No', canceling the shutdown.mp3")
            
            else:
                # Kalo dibangunin biasa
                play_recording("I'm awake and ready for commands.", "voice/I'm awake and ready for commands.mp3")
        else:
            pass
        continue
    
    # PERINTAH MASUK MODE IDLE
    
    elif "go to sleep" in perintah or "standby" in perintah or "sleep" in perintah:
        idle_mode = True 
        play_recording("Alright, I'm going to sleep. Just say wake up if you need me.", "voice/Alright, I'm going to sleep, Just say wake up if you need me.mp3")
        continue

    
    # PERINTAH BUKA APLIKASI
    
    if "open whatsapp" in perintah or "open whats app" in perintah:
        play_recording("Okay, opening WhatsApp.", "voice/Okay, opening WhatsApp.mp3")
        os.system("start whatsapp:")
        
    elif "open youtube" in perintah:
        play_recording("Alright, going to YouTube.", "voice/Alright, going to YouTube.mp3")
        webbrowser.open("https://www.youtube.com")
        
    elif "open settings" in perintah:
        play_recording("Opening Windows Settings.", "voice/Opening Windows Settings.mp3")
        os.system("start ms-settings:")
    
    elif "open file manager" in perintah or "open explorer" in perintah:
        play_recording("Opening File Manager.", "voice/Opening File Manager.mp3")
        os.system("start explorer")
        
    elif "open chrome" in perintah:
        play_recording("Opening Chrome.", "voice/Opening chrome.mp3")
        os.system("start chrome")
        
    elif "open music" in perintah or "open youtube music" in perintah:
        play_recording("Opening Youtube Music.", "voice/Opening Youtube Music.mp3")
        alamat_aplikasi = r"D:\Appx\YouTube-Music-3.7.2.exe"
        os.startfile(alamat_aplikasi)
        
    elif "open google" in perintah:
        play_recording("Opening Google.", "voice/Opening Google.mp3")
        webbrowser.open("https://www.google.com/?hl=ID")
        
    elif "open tik tok" in perintah or "open tiktok" in perintah:
        play_recording("Opening TikTok.", "voice/Opening TikTok.mp3")
        webbrowser.open("https://www.tiktok.com/foryou")
        
    elif "open instagram" in perintah:
        play_recording("Opening Instagram.", "voice/Opening Instagram.mp3")
        webbrowser.open("https://www.instagram.com/")
        
    
    # PERINTAH TUTUP APLIKASI
    
    elif "close whatsapp" in perintah or "close what" in perintah or "open whats app" in perintah:
        cek_wa = os.popen('tasklist /fi "WINDOWTITLE eq WhatsApp*"').read().lower()
        if "no tasks" not in cek_wa:
            play_recording("Okay, closing WhatsApp.", "voice/Okay, closing WhatsApp.mp3")
            os.system('taskkill /f /fi "WINDOWTITLE eq WhatsApp*"') 
        else:
            play_recording("Sorry, WhatsApp is already closed.", "voice/Sorry, WhatsApp is already closed.mp3")
            
    elif "close settings" in perintah or "close setting" in perintah:
        daftar_aplikasi = os.popen('tasklist').read()
        if "SystemSettings.exe" in daftar_aplikasi:
            play_recording("Closing Windows Settings.", "voice/Closing Windows Settings.mp3")
            os.system("taskkill /im SystemSettings.exe /f")
        else:
            play_recording("Sorry, Settings is not open right now.", "voice/Sorry, Settings is not open right now.mp3")
            
    elif "close help" in perintah :
        daftar_aplikasi = os.popen('tasklist').read()
        if "Notepad.exe" in daftar_aplikasi:
            play_recording("Closing help.", "voice/Closing help.mp3")
            os.system("taskkill /im Notepad.exe /f")
        else:
            play_recording("Sorry, help is not open right now.", "voice/Sorry, help is not open right now.mp3")
            
    elif "close music" in perintah or "close youtube music" in perintah:
        daftar_aplikasi = os.popen('tasklist').read()
        if "YouTube-Music-3.7.2.exe" in daftar_aplikasi or "YouTube Music.exe" in daftar_aplikasi:
            play_recording("Closing Youtube Music.", "voice/Closing Youtube Music.mp3")
            os.system("taskkill /im YouTube-Music-3.7.2.exe /f")
            os.system('taskkill /im "YouTube Music.exe" /f')
        else:
            play_recording("Sorry, youtube music is not open right now.", "voice/Sorry, youtube music is not open right now.mp3")
            
    elif "kill chrome" in perintah or "kill google chrome" in perintah:
        daftar_aplikasi = os.popen('tasklist').read().lower()
        if "chrome.exe" in daftar_aplikasi:
            play_recording("Alright, killing Google Chrome.", "voice/Alright, killing Google Chrome.mp3") 
            os.system("taskkill /im chrome.exe /f")
        else:
            play_recording("Google Chrome is already closed, Neev.", "voice/Google Chrome is already closed.mp3")
            
    elif "close chrome" in perintah or "close google chrome" in perintah:
        daftar_aplikasi = os.popen('tasklist').read().lower()
        
        if "chrome.exe" in daftar_aplikasi:
            play_recording("Alright, closing Google Chrome gracefully.", "voice/Alright, closing Google Chrome gracefully.mp3") 
            
            # Spell PowerShell buat ngeklik 'X' secara halus
            mantra_sopan_chrome = 'powershell -command "Get-Process chrome | Where-Object {$_.MainWindowHandle -ne 0} | ForEach-Object { $_.CloseMainWindow() }"'
            os.system(mantra_sopan_chrome)
            
        else:
            play_recording("Google Chrome is already closed.", "voice/Google Chrome is already closed.mp3")
    
    elif "close file manager" in perintah or "close explorer" in perintah:
        # Panggil radar powershell buat ngitung ada berapa jendela folder yang lagi kebuka
        jumlah_folder = os.popen('powershell -command "@((New-Object -comObject Shell.Application).Windows()).Count"').read().strip()
        
        # Kalo jumlahnya bukan 0 beraryi ada folder yang lagi buka
        if jumlah_folder != "0" and jumlah_folder != "":
            play_recording("Closing File Manager.", "voice/Closing File Manager.mp3")
            mantra_tutup_folder = 'powershell -command "(New-Object -comObject Shell.Application).Windows() | foreach-object {$_.quit()}"'
            os.system(mantra_tutup_folder)
        else:
            # Kalo jendelanya 0 (udah ketutup semua)
            play_recording("File Manager is already closed.", "voice/File Manager is already closed.mp3")

    # PERINTAH MINIMIZE 
    
    elif "minimize chrome" in perintah or "minimize google chrome" in perintah:
        daftar_aplikasi = os.popen('tasklist').read().lower()
        
        if "chrome.exe" in daftar_aplikasi:
            play_recording("Alright, minimizing Google Chrome.", "voice/Alright, minimizing Google Chrome.mp3")
            mantra_minimize_chrome = 'powershell -command "$w = Add-Type -Name W -PassThru -MemberDefinition \'[DllImport(\\"user32.dll\\")] public static extern bool ShowWindowAsync(IntPtr h, int c);\'; Get-Process | Where-Object {$_.ProcessName -match \'chrome\' -and $_.MainWindowHandle -ne 0} | ForEach-Object { $w::ShowWindowAsync($_.MainWindowHandle, 2) }"'
            os.system(mantra_minimize_chrome)
            
        else:
            play_recording("Google Chrome is not open right now, Neev.", "voice/Google Chrome is not open right now.mp3")

    elif "minimize whatsapp" in perintah or "minimize whats app" in perintah:
        cek_wa = os.popen('tasklist /fi "WINDOWTITLE eq WhatsApp*"').read().lower()
        if "no tasks" not in cek_wa:
            play_recording("Okay, closing WhatsApp.", "voice/Okay, closing WhatsApp.mp3")
            
            # Spell Remote Control buat mencet tombol minimize (-)
            mantra_minimize_wa = 'powershell -command "$w = Add-Type -Name W -PassThru -MemberDefinition \'[DllImport(\\"user32.dll\\")] public static extern bool ShowWindowAsync(IntPtr h, int c);\'; Get-Process | Where-Object {$_.MainWindowTitle -match \'WhatsApp\' -and $_.MainWindowHandle -ne 0} | ForEach-Object { $w::ShowWindowAsync($_.MainWindowHandle, 2) }"'
            os.system(mantra_minimize_wa)
        else:
            play_recording("WhatsApp is not open right now, Neev.", "voice/Sorry, WhatsApp is already closed.mp3")
        
    # PERINTAH NEEVERA SELF 
    
    elif "hide yourself" in perintah or "minimize yourself" in perintah:
        play_recording("Alright, hiding myself in the background.", "voice/Alright, hiding myself in the background.mp3")
        
        # Python ngambil jendela terminalnya sendiri, trs angka '6' artinya "Minimize"
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)
    
    # PERINTAH SHOW NEEVERA (MUNCULKAN DIRI SENDIRI)
    
    elif "show yourself" in perintah or "come back" in perintah:
        play_recording("Alright, I am back on your screen.", "voice/Alright, I am back on your screen.mp3")
        
        # Angka '9' di sini sandi Windows buat restore (kembalikan jendela seperti semula)
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 9)

    # PERINTAH MINIMIZE SEMUA APLIKASI
    
    elif "minimize apps" in perintah or "minimize everything" in perintah:
        play_recording("Alright, minimizing all applications.", "voice/Alright, minimizing all applications.mp3")
        os.system('powershell -command "(New-Object -ComObject Shell.Application).MinimizeAll()"')
    
    # PERINTAH MENCARI DI INTERNET
    
    elif "search on youtube" in perintah or "on youtube" in perintah:
        play_recording("What do you want to search on YouTube?", "voice/What do you want to search on YouTube.mp3")
        keyword = dengar_google()
        print("Keyword:", keyword)
        play_recording("Alright, searching now.", "voice/Alright_Searching_Now.mp3") 
        webbrowser.open("https://www.youtube.com/results?search_query=" + keyword)

    elif "search on tiktok" in perintah or "search on tik tok" in perintah or "on tik tok" in perintah:
        play_recording("What do you want to search on TikTok?", "voice/What do you want to search on TikTok.mp3")
        keyword = dengar_google()
        print("Keyword:", keyword)
        play_recording("Alright, searching now.", "voice/Alright_Searching_Now.mp3")
        webbrowser.open("https://www.tiktok.com/search?q=" + keyword)
        
    elif "search on google" in perintah or "on google" in perintah:
        play_recording("What do you want to search on Google?", "voice/What do you want to search on Google.mp3")
        keyword = dengar_google()
        print("Keyword:", keyword)
        play_recording("Alright, searching now.", "voice/Alright_Searching_Now.mp3")
        webbrowser.open("https://www.google.com/search?q=" + keyword)
    
    # Deteksi pencarian berita/kejadian terkini di Indonesia untuk membuka beberapa portal berita nasional sekaligus
    elif "what is happening in my country" in perintah or "what is happening" in perintah or "indonesia news" in perintah or "national news" in perintah:
        ngomong_langsung("Opening top Indonesian national news portals for the latest updates.")
        webbrowser.open("https://news.detik.com/")
        webbrowser.open("https://www.kompas.com/")
        webbrowser.open("https://www.cnnindonesia.com/")
        webbrowser.open("https://www.tempo.co/")
        
    # PERINTAH WIFI 
    
    elif "turn on wifi" in perintah:
        play_recording("Turning on Wi-Fi.", "voice/Turning on Wi-Fi.mp3")
        # CMD buat nyalain WiFi
        os.system('netsh interface set interface "Wi-Fi" admin=enabled')
        
    elif "turn off wifi" in perintah:
        play_recording("Turning off Wi-Fi.", "voice/Turning off Wi-Fi.mp3")
        # CMD buat matiin WiFi
        os.system('netsh interface set interface "Wi-Fi" admin=disabled')

    
    # PERINTAH HOTSPOT
    
    elif "hotspot" in perintah or "open hotspot" in perintah:
        play_recording("Opening Mobile Hotspot settings.", "voice/Opening Mobile Hotspot settings.mp3")
        # Buka halaman pengaturan Hotspot
        os.system("start ms-settings:network-mobilehotspot")

    
    # TUTUP SEMUA APPS
    
    elif "close apps" in perintah:
        play_recording("Alright Neev, cleaning up your workspace.", "voice/Alright Neev, cleaning up your workspace.mp3")
        os.system("taskkill /im chrome.exe >nul 2>&1")
        mantra_sapu_jagat = "powershell -command \"Get-Process | Where-Object {$_.MainWindowHandle -ne 0 -and $_.ProcessName -notmatch 'explorer|Code|cmd|WindowsTerminal|powershell|python|Taskmgr|chrome'} | Stop-Process -Force -ErrorAction SilentlyContinue\""
        os.system(mantra_sapu_jagat)
        play_recording("Workspace cleared! All done.", "voice/Workspace_cleared!_All_done.mp3")

    
    # IDENTITAS & SAPAAN
    
    elif "who are you" in perintah:
        voice_options = [
            "voice/I am Neevera your Personal Assistant.mp3",
            "voice/I am Neevera, Ready to help you.mp3",
        ]
        random_voice = random.choice(voice_options)
        text = random_voice.replace(".mp3", "").replace("_", " ").replace("voice/", "")
        play_recording(text, random_voice)
        
    elif "hello" in perintah or "hey" in perintah or "neevera" in perintah or "hey neevera" in perintah or "neev era" in perintah or "era" in perintah:
        pilihan_jawaban = [
            "voice/Yes Neev I am here.mp3",
            "voice/Hello Neev What can I do for you today.mp3",
            "voice/Neevera is listening Tell me your command.mp3",
            "voice/Hi there Neevera here Need any help.mp3"
        ]
        random_voice = random.choice(pilihan_jawaban)
        text = random_voice.replace(".mp3", "").replace("_", " ").replace("voice/", "")
        play_recording(text, random_voice)
        
    elif "how are you" in perintah or "are you good" in perintah :
        pilihan_jawaban = [
            "voice/I'm doing well, How about you Is there something you'd like to do.mp3",
            "voice/I'm good! How about you Anything you want to do.mp3",
            "voice/I'm fine, How about you What would you like to do.mp3"
        ]
        random_voice = random.choice(pilihan_jawaban)
        text = random_voice.replace(".mp3", "").replace("_", " ").replace("voice/", "")
        play_recording(text, random_voice)
        
    elif "who is your bos" in perintah or "who made you" in perintah or "who created you" in perintah or "who built you" in perintah or "creator" in perintah or "hanif" in perintah or "neev" in perintah:
        play_recording("I was created by Neev, also known as Hanif. He is a very kind and cool person.", "voice/I was created by Neev, also known as Hanif. He is a very kind and cool person.mp3")
        
    
    # PERTANYAAN PROGRAM BISA NGAPAIN AJA
    
    elif "what can you do" in perintah:
        play_recording("I am equipped to handle everything from application management to core system controls and web browsing, I'm constantly learning new things, Just say 'Help', and I will show you exactly what I can do for you today", "voice/I am equipped to handle everything from application management to core system controls and web browsing, I'm constantly learning new things, Just say 'Help', and I will show you exactly what I can do for you today.mp3")
        
    
    # HELP
    
    elif "help" in perintah:
        play_recording("Opening the list of available commands for you", "voice/Opening the list of available commands for you.mp3")
        os.system("start notepad commands.txt")
    
    
    # EXIT
    
    elif "exit" in perintah or "stop" in perintah:
        play_recording("Goodbye Neev, See you later, I look forward to assisting you again! bye bye","voice/Goodbye Neev, See you later, I look forward to assisting you again! bye bye.mp3")
        break 
    
    
    # DETEKSI APLIKASI/PLATFORM BELUM TERDAFTAR
    
    elif "open" in perintah:
        play_recording("Sorry, I can't open that yet because the application is not registered in my system.", "voice/Sorry, I can't open that yet because the application is not registered in my system.mp3")
        
    elif "close" in perintah:
        play_recording("Sorry, I can't close that yet because the application is not registered in my system.", "voice/Sorry, I can't close that yet because the application is not registered in my system.mp3")
        
    elif "search on" in perintah:
        play_recording("Sorry, I can't search on that platform yet because it's not registered in my system.", "voice/Sorry, I can't open that yet because the application is not registered in my system.mp3")
        
    
    # PERINTAH SCREENSHOT 
    
    elif "screenshot" in perintah or "capture screen" in perintah or "capture" in perintah:
        play_recording("Taking a screenshot.", "voice/Taking a screenshot.mp3")
        # Wajib pakai huruf 'r' di depan tanda kutip
        alamat_folder = r"C:\Users\LENOVO\Downloads"
        
        # Bikin nama filenya dari jam dan tanggal
        waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nama_file = f"screenshot_{waktu_sekarang}.png"
        alamat_lengkap = os.path.join(alamat_folder, nama_file)
        foto = pyautogui.screenshot()
        foto.save(alamat_lengkap)
        
        play_recording("Screenshot saved successfully.", "voice/Screenshot saved successfully.mp3")
        print(f"[System: Screenshot berhasil disimpan di {alamat_lengkap}]")
        
    
    # PERINTAH CEK BATERAI
    
    elif "battery" in perintah or "check battery" in perintah or "battery status" in perintah:
        baterai = psutil.sensors_battery()
        persen = baterai.percent
        ngecas = baterai.power_plugged # Bernilai True kalau charger dipasang
        
        if ngecas:
            ngomong_langsung(f"This is the co-assistant of Neevera. Your battery is at {persen} percent and currently charging")
        elif persen < 20:
            ngomong_langsung(f"This is the co-assistant of Neevera. Warning Neev! Your battery is only at {persen} percent. Please plug in the charger immediately.")
        else:
            ngomong_langsung(f"This is the co-assistant of Neevera. Your battery is at {persen} percent.")
  
    # PERINTAH CEK JAM
    
    elif "what time is it" in perintah or "check time" in perintah :
        jam_sekarang = datetime.datetime.now().strftime("%I:%M %p")
        ngomong_langsung(f"This is the co-assistant of Neevera. It is currently {jam_sekarang}")

    # PERINTAH CEK HARI INI
    
    elif "what day is it" in perintah or "what day is today" in perintah:
        hari_ini = datetime.datetime.now().strftime("%A")
        ngomong_langsung(f"This is the co-assistant of Neevera. Today is {hari_ini}")

    # PERINTAH LOCK SCREEN (DENGAN KONFIRMASI)
    
    elif "lock my computer" in perintah or "lock screen" in perintah:
        # Nanya dulu buat mastiin
        play_recording("Are you sure you want to lock the computer?\n[System: say 'Yes lock my computer'/sure or 'No/Cancel']\n", "voice/Are you sure you want to lock the computer.mp3")
        
        # Buka telinga sebentar buat nungguin jawaban
        jawaban = dengar_vosk().lower()
        print("You answered:", jawaban)
        
        # Kalo dijawab Yes
        if "yes lock my computer" in jawaban or "sure" in jawaban:
            play_recording("Locking your computer now.", "voice/Locking your computer now.mp3")
            # Eksekusi kunci layar
            os.system("rundll32.exe user32.dll,LockWorkStation")
            
        # Kalo berubah pikiran (No)
        elif "no" in jawaban or "cancel" in jawaban:
            play_recording("Lock screen canceled, I am still here.", "voice/Lock screen canceled, I am still here.mp3")
            
        # Jaga-jaga kalo suaranya ga jelas
        else:
            play_recording("I didn't catch a clear 'Yes' or 'No', canceling the lock screen.", "voice/I didn't catch a clear yes or no, canceling the lock screen.mp3")

    # PERINTAH SHUTDOWN (MASUK STANDBY DULU)
    
    elif "shutdown the computer" in perintah or "turn off the computer" in perintah:
        konfirmasi_shutdown = True # Nyalain saklar bahaya
        idle_mode = True # Langsung ke mode idle
        play_recording("Are you sure? I am entering standby mode to prevent accidental shutdown. Wake me up first to confirm.", "voice/Are you sure I am entering standby mode to prevent accidental shutdown. Wake me up first to confirm.mp3")
        continue # Langsung lempar ke atas biar masuk mode idle
    
    # DEFAULT (JIKA MODE NEEVERA TIDAK MENGENALI PERINTAH)
    
    else:
        play_recording("Sorry, I don't understand that command. Say Red to switch to LLM mode.", "voice/Sorry, I don't understand that command.mp3")