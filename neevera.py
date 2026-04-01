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

# SUARA PYGAME

pygame.mixer.init()

# SETUP TEXT-TO-SPEECH (ANTI-MOGOK)

def ngomong_langsung(teks):
    print("Assistant: " + teks)
    mantra_ngomong = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{teks}\')"'
    os.system(mantra_ngomong)

# SETUP VOSK (TELINGA BARU)

q = queue.Queue()

# GOOGLE SPEECH RECOGNIZER
telinga = sr.Recognizer()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = Model("model")  
rec = KaldiRecognizer(model, 16000, '''
[   
    "okay",
    "alright",
    "aight",
    "so",
    "are you good",
    "how are you",
    "go to sleep",
    "open",
    "minimize",
    "open whatsapp",
    "open youtube",
    "open settings",
    "open whats app",
    "open instagram",
    "open music",
    "open youtube music",
    "open file manager",
    "explorer",
    "close",
    "close whatsapp",
    "close settings",
    "close file manager",
    "close chrome",
    "close google chrome",
    "search on",
    "search on youtube",
    "search on tiktok",
    "search on tik tok",
    "close apps",
    "who are you",
    "hello",
    "help",
    "exit",
    "stop",
    "hey neevera",
    "neevera",
    "neev era",
    "neev",
    "era",
    "what can you do",
    "standby",
    "wake up",
    "who built you",
    "who is your bos",
    "who created you",
    "who made you",
    "turn on wifi",
    "hotspot",
    "turn off wifi",
    "screenshot",
    "check battery",
    "battery status",
    "what time is it",
    "capture screen"
]
''')

def dengar_google():
    with sr.Microphone() as sumber:
        print("Listening keyword (Online mode)...")
        telinga.pause_threshold = 1.5 
        telinga.adjust_for_ambient_noise(sumber, duration=0.5)
        
        try:
            audio = telinga.listen(sumber, timeout=8)
            teks = telinga.recognize_google(audio, language="id-ID")
            return teks
        except sr.WaitTimeoutError:
            print("[System: Neev has been quiet for too long, search cancelled]")
            return ""
        except:
            print("[System: Voice is unclear or there is an internet connection issue]")
            return ""

def dengar_vosk():
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype='int16', channels=1, callback=callback):
        print("\nListening...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                hasil = json.loads(rec.Result())
                return hasil.get("text", "")

# FUNCTION TO PLAY CUSTOM MP3 RECORDINGS

def play_recording(screen_text, mp3_file_name):
    print("Assistant: " + screen_text)
    
    try:
        
        pygame.mixer.music.load(mp3_file_name)
        pygame.mixer.music.set_volume(1.0) 
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except:
        print("[System Error: Oops, the file " + mp3_file_name + " is missing!]")

# STARTUP VOICE

play_recording("Hello! Neevera here.", "voice/Hello, Neevera here!.mp3")

print("\n[System: Voice assistant is starting, say 'Help' to see the commands]")

# PROGRAM UTAMA

idle_mode = False
while True:
    try:
        teks = dengar_vosk()
        perintah = teks.lower()
        print("You said:", perintah)

        if perintah == "":
            continue

    except:
        print("Error listening...")
        continue
    
    # LOGIKA MODE IDLE (TIDUR)
    
    if idle_mode == True:
        if "wake up" in perintah:
            idle_mode = False # 
            play_recording("I'm awake and ready for commands.", "voice/I'm awake and ready for commands.mp3")
        else:
            pass
        continue 
        
    
    # PERINTAH MASUK MODE IDLE
    
    elif "go to sleep" in perintah or "standby" in perintah:
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
        play_recording("Opening Google Chrome.", "voice/Opening chrome.mp3")
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
            
    elif "minimize chrome" in perintah or "minimize google chrome" in perintah:
        # Minta absen daftar aplikasi dulu, jadiin huruf kecil semua
        daftar_aplikasi = os.popen('tasklist').read().lower()
        
        # Misal chrome beneran ada di daftar
        if "chrome.exe" in daftar_aplikasi:
            play_recording("Alright, minimizing Google Chrome.", "voice/Alright, minimizing Google Chrome.mp3") 
            os.system("taskkill /im chrome.exe /f")
        else:
            # Kalau chrome udah ketutup
            play_recording("Google Chrome is already closed, Neev.", "voice/Google Chrome is already closed.mp3")
            
    elif "close chrome" in perintah or "close google chrome" in perintah:
        daftar_aplikasi = os.popen('tasklist').read().lower()
        
        if "chrome.exe" in daftar_aplikasi:
            play_recording("Alright, closing Google Chrome gracefully.", "voice/Alright, closing Google Chrome gracefully.mp3") 
            
            # Mantra PowerShell buat ngeklik 'X' secara halus
            mantra_sopan_chrome = 'powershell -command "Get-Process chrome | Where-Object {$_.MainWindowHandle -ne 0} | ForEach-Object { $_.CloseMainWindow() }"'
            os.system(mantra_sopan_chrome)
            
        else:
            play_recording("Google Chrome is already closed.", "voice/Google Chrome is already closed.mp3")
    
    elif "minimize whatsapp" in perintah or "minimize whats app" in perintah:
        cek_wa = os.popen('tasklist /fi "WINDOWTITLE eq WhatsApp*"').read().lower()
        if "no tasks" not in cek_wa:
            play_recording("Okay, closing WhatsApp.", "voice/Okay, closing WhatsApp.mp3")
            
            # Mantra Remote Control buat mencet tombol Minimize (-)
            mantra_minimize_wa = 'powershell -command "$w = Add-Type -Name W -PassThru -MemberDefinition \'[DllImport(\\"user32.dll\\")] public static extern bool ShowWindowAsync(IntPtr h, int c);\'; Get-Process | Where-Object {$_.MainWindowTitle -match \'WhatsApp\' -and $_.MainWindowHandle -ne 0} | ForEach-Object { $w::ShowWindowAsync($_.MainWindowHandle, 2) }"'
            os.system(mantra_minimize_wa)
        else:
            play_recording("WhatsApp is not open right now, Neev.", "voice/Sorry, WhatsApp is already closed.mp3")
    
    elif "close file manager" in perintah or "close explorer" in perintah:
        # Panggil radar PowerShell buat ngitung ada berapa jendela folder yang lagi kebuka
        jumlah_folder = os.popen('powershell -command "@((New-Object -comObject Shell.Application).Windows()).Count"').read().strip()
        
        # Kalau jumlahnya bukan 0 beraryi ada folder yang lagi buka
        if jumlah_folder != "0" and jumlah_folder != "":
            play_recording("Closing File Manager.", "voice/Closing File Manager.mp3")
            mantra_tutup_folder = 'powershell -command "(New-Object -comObject Shell.Application).Windows() | foreach-object {$_.quit()}"'
            os.system(mantra_tutup_folder)
        else:
            # Kalau jendelanya 0 (udah ketutup semua)
            play_recording("File Manager is already closed.", "voice/File Manager is already closed.mp3")
        
            
    
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
    
    
    # PERINTAH WI-FI 
    
    elif "turn on wifi" in perintah:
        play_recording("Turning on Wi-Fi.", "voice/Turning on Wi-Fi.mp3")
        # Jurus CMD buat nyalain Wi-Fi
        os.system('netsh interface set interface "Wi-Fi" admin=enabled')
        
    elif "turn off wifi" in perintah:
        play_recording("Turning off Wi-Fi.", "voice/Turning off Wi-Fi.mp3")
        # Jurus CMD buat matiin Wi-Fi
        os.system('netsh interface set interface "Wi-Fi" admin=disabled')

    
    # PERINTAH HOTSPOT
    
    elif "hotspot" in perintah or "open hotspot" in perintah:
        play_recording("Opening Mobile Hotspot settings.", "voice/Opening Mobile Hotspot settings.mp3")
        # Buka halaman pengaturan Hotspot
        os.system("start ms-settings:network-mobilehotspot")

    
    # TUTUP SEMUA APPS
    
    elif "close apps" in perintah:
        play_recording("Alright Neev, cleaning up your workspace.", "voice/Alright Neev, cleaning up your workspace.mp3")
        mantra_sapu_jagat = "powershell -command \"Get-Process | Where-Object {$_.MainWindowHandle -ne 0 -and $_.ProcessName -notmatch 'explorer|Code|cmd|WindowsTerminal|powershell|python|Taskmgr'} | Stop-Process -Force -ErrorAction SilentlyContinue\""
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
        
    elif "who is your bos" in perintah or "who made you" in perintah or "who created you" in perintah or "who built you" in perintah:
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
        play_recording("Sorry, I can't close that yet because the application is not registered in my system.", "voice/Sorry, I can't open that yet because the application is not registered in my system.mp3")
        
    elif "search on" in perintah:
        play_recording("Sorry, I cannot search on that platform yet because it's not registered in my system.", "voice/Sorry, I can't open that yet because the application is not registered in my system.mp3")
        
    
    # PERINTAH SCREENSHOT 
    
    elif "screenshot" in perintah or "capture screen" in perintah or "capture" in perintah:
        play_recording("Taking a screenshot.", "voice/Taking a screenshot.mp3")
        #Wajib pakai huruf 'r' di depan tanda kutip
        alamat_folder = r"C:\Users\LENOVO\Downloads"
        
        # 2. Bikin nama filenya dari jam dan tanggal
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
            ngomong_langsung(f"This is the co-assistant of Neevera. Your battery is at {persen} percent and currently charging, Neev.")
        elif persen < 20:
            ngomong_langsung(f"This is the co-assistant of Neevera. Warning Neev! Your battery is only at {persen} percent. Please plug in the charger immediately.")
        else:
            ngomong_langsung(f"This is the co-assistant of Neevera. Your battery is at {persen} percent.")
  
    # PERINTAH CEK JAM
    
    elif "what time is it" in perintah or "check time" in perintah :
        jam_sekarang = datetime.datetime.now().strftime("%I:%M %p")
        ngomong_langsung(f"This is the co-assistant of Neevera. It is currently {jam_sekarang}, Neev.")
    
    # DEFAULT
    
    else:
        play_recording("Sorry, I don't understand that command.", "voice/Sorry, I don't understand that command.mp3")