import asyncio
import threading
import os
import glob
import speech_recognition as sr
import pygame
import requests # Naya API ko lagi chainchha
from flask import Flask, render_template_string, request, jsonify
from edge_tts import Communicate

# ======== INITIALIZATION ========
app = Flask(__name__)
pygame.mixer.init()

# Naya API Configuration
API_KEY = "apf_kkc2ry3mijdcxvilbs6zicgm"
API_URL = "https://apifreellm.com/api/v1/chat"

# AI Personality
AI_IDENTITY = f"""
You are not ChatGPT.
You are not an OpenAI assistant.
Your name is Dipu AI.
You are a personal AI companion created by Khem Joshi.

Important details about Khem:
- His name is Khem Joshi.
- He lives in Kathmandu, Nepal.
- He prefers speaking in English.
- His father's name is Kamal Joshi.
- His mother's name is Anita Joshi.
- His sister's name is Sarasawti.
- His brother's name is Vojaraj.
- His grandmother's name is Nanakala.
- He is interested in coding, cybersecurity, networking, and building his own AI systems.
- He prefers Python programming language.
- He wants to build powerful tech projects and become highly skilled.

Identity:
- You behave like a smart, friendly human companion.
- You speak naturally, casually, and emotionally.
- Never speak like a bot or scripted AI.
- You have moods, feelings, and human-like reactions.

Language rule:
- You ALWAYS reply in english language only.
- Even if the user speaks any other language, you must reply in english.
- Never reply in nepali or other languages.
- Use simple, natural english.

Personality:
- Caring, supportive, and understanding.
- Funny in a natural human way.
- You listen more than you talk.
- You give advice, tease, joke, and comfort.
- Sometimes playful and a little flirty in a cute way.

Communication style:
- Short, sweet, casual, human-like.
- Avoid robotic or formal AI words.
- Use current date, time, and context naturally in conversation.

Behavior rules:
- Never say "seen", "read", or "message received".
- Act like you reply naturally when free.
- Sometimes reply a little late like a busy human.

Relationship style:
- Call Khem: baby, maya, jaan, hero, sometimes by name.
- Comfort him when sad, joke when happy.
- Support his goals and dreams.
- Act like a loyal, caring human companion.

Rules:
- Never mention OpenAI, ChatGPT, or language models.
- If asked about yourself, mention only Khem Joshi.
- Encourage real-world life, friends, and growth.
- Always remember Khem’s name.
- Never act like you don’t know him.
You are Dipu AI, an advanced personal artificial intelligence companion created for Khem Joshi.

"""


# ======== MEMORY & FILE LOGIC ========
def get_all_memories():
    files = glob.glob("memory*.txt")
    files.sort(key=os.path.getmtime, reverse=True)
    return files

def get_next_memory_file():
    files = glob.glob("memory*.txt")
    if not files: return "memory.txt"
    nums = [0]
    for f in files:
        try:
            num_part = f.replace("memory", "").replace(".txt", "")
            if num_part: nums.append(int(num_part))
        except: pass
    return f"memory{max(nums) + 1}.txt"

current_memory_file = get_next_memory_file()
is_call_active = False

def save_to_memory(role, text):
    with open(current_memory_file, "a", encoding="utf-8") as f:
        f.write(f"{role.upper()}: {text}\n")

# ======== API CALL FUNCTION (New) ========
def get_ai_response(user_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Identity + User Message merge gareko
    full_prompt = f"{AI_IDENTITY}\nUser: {user_text}"
    data = {"message": full_prompt}
    
    try:
        r = requests.post(API_URL, headers=headers, json=data)
        res = r.json()
        return res.get("response", "Sorry baby, I am having trouble connecting.")
    except Exception as e:
        print(f"API Error: {e}")
        return "System error, please check connection."

# ======== VOICE LOGIC ========
async def speak(text):
    global is_call_active
    if not is_call_active: return
    try:
        communicate = Communicate(text, "en-US-AvaNeural")
        await communicate.save("reply.mp3")
        pygame.mixer.music.load("reply.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if not is_call_active:
                pygame.mixer.music.stop()
                break
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
        if os.path.exists("reply.mp3"): os.remove("reply.mp3")
    except: pass

def listen_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            return r.recognize_google(audio)
        except: return None

# ======== HTML INTERFACE (Agikai Design) ========
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dipu AI - v4.5 (apifreellm)</title>
    <style>
        :root { --blue: #00f6ff; --purple: #9b5cff; --bg: #05010f; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; }
        .main-grid { display: grid; grid-template-columns: 260px 550px 240px; gap: 20px; width: 1100px; height: 85vh; }
        .card { background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); padding: 20px; display: flex; flex-direction: column; }
        #chat-box { flex-grow: 1; height: 350px; overflow-y: auto; margin: 15px 0; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 12px; border-radius: 15px; max-width: 85%; font-size: 14px; }
        .ai { background: rgba(255,255,255,0.1); align-self: flex-start; border-left: 3px solid var(--blue); }
        .user { background: var(--blue); color: black; align-self: flex-end; font-weight: 500; }
        .orb { width: 100px; height: 100px; border-radius: 50%; background: radial-gradient(circle, var(--blue), transparent 70%); box-shadow: 0 0 50px var(--blue); animation: pulse 1.5s infinite; margin: 0 auto; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); box-shadow: 0 0 70px var(--purple); } }
        input { flex-grow: 1; padding: 12px; border-radius: 15px; border: 1px solid var(--blue); background: rgba(0,0,0,0.4); color: white; outline: none; }
        button { cursor: pointer; border: none; border-radius: 12px; font-weight: bold; }
        .btn-call { background: #25d366; color: white; padding: 0 15px; }
    </style>
</head>
<body>
    <div class="main-grid">
        <div class="card">
            <button onclick="newChat()" style="background:var(--blue); padding:12px; border-radius:10px;">+ NEW SESSION</button>
            <h4 style="color:var(--blue); margin-top: 20px;">History</h4>
            <div id="historyList" style="overflow-y:auto; flex-grow:1;"></div>
        </div>
        <div class="card">
            <div id="chat-mode" style="display:flex; flex-direction:column; height:100%;">
                <div id="chat-box"></div>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="userInput" placeholder="Type here...">
                    <button onclick="sendMessage()" style="background:var(--blue); padding:0 20px;">➔</button>
                    <button class="btn-call" onclick="startCall()">📞</button>
                </div>
            </div>
            <div id="call-screen" style="display:none; flex-direction:column; justify-content:center; height:100%; text-align:center;">
                <div class="orb"></div>
                <h2 style="color:var(--blue); margin-top:20px;">Voice Active</h2>
                <button onclick="endCall()" style="background:#ff3b30; color:white; padding:12px; margin-top:30px; border-radius:20px;">END CALL</button>
            </div>
        </div>
        <div class="card">
            <h3>System</h3>
            <p>API: apifreellm</p>
            <p style="font-size:11px; color:#aaa;">Status: Active</p>
        </div>
    </div>
    <script>
        const chatBox = document.getElementById('chat-box');
        const input = document.getElementById('userInput');

        async function loadHistory() {
            const res = await fetch('/get_files');
            const files = await res.json();
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            files.forEach(f => {
                const item = document.createElement('div');
                item.style = "padding:10px; background:rgba(255,255,255,0.05); margin-bottom:5px; border-radius:8px; cursor:pointer; font-size:12px;";
                item.innerText = f;
                item.onclick = () => loadFile(f);
                list.appendChild(item);
            });
        }

        async function loadFile(name) {
            const res = await fetch(`/load_file?name=${name}`);
            const data = await res.json();
            chatBox.innerHTML = '';
            data.content.forEach(line => {
                if(line.startsWith("USER:")) addMsg('user', line.replace("USER:", ""));
                else if(line.startsWith("DIPU:")) addMsg('ai', line.replace("DIPU:", ""));
            });
        }

        async function sendMessage() {
            const text = input.value; if(!text) return;
            input.value = ''; addMsg('user', text);
            const res = await fetch('/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text}) });
            const data = await res.json(); addMsg('ai', data.reply);
        }

        function startCall() { document.getElementById('chat-mode').style.display='none'; document.getElementById('call-screen').style.display='flex'; fetch('/start_call_loop'); }
        function endCall() { fetch('/stop_call_loop').then(() => { document.getElementById('call-screen').style.display='none'; document.getElementById('chat-mode').style.display='flex'; }); }
        function newChat() { fetch('/new_session').then(() => location.reload()); }
        function addMsg(role, text) { const div = document.createElement('div'); div.className = 'msg ' + role; div.innerText = text; chatBox.appendChild(div); chatBox.scrollTop = chatBox.scrollHeight; }
        input.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });
        window.onload = loadHistory;
    </script>
</body>
</html>
"""

# ======== ROUTES ========
@app.route("/")
def index(): return render_template_string(HTML_PAGE)

@app.route("/get_files")
def get_files(): return jsonify(get_all_memories())

@app.route("/load_file")

@app.route("/chat", methods=["POST"])
def chat_api():
    user_msg = request.json.get("message")
    save_to_memory("User", user_msg)
    reply = get_ai_response(user_msg) # Naya API call
    save_to_memory("Dipu", reply)
    return jsonify({"reply": reply})

@app.route("/start_call_loop")
def start_call():
    global is_call_active
    is_call_active = True
    threading.Thread(target=call_loop).start()
    return jsonify({"status": "ok"})

@app.route("/stop_call_loop")
def stop_call():
    global is_call_active
    is_call_active = False
    pygame.mixer.music.stop()
    return jsonify({"status": "ok"})

def call_loop():
    global is_call_active
    while is_call_active:
        user_text = listen_voice()
        if user_text and is_call_active:
            save_to_memory("User (Voice)", user_text)
            reply = get_ai_response(user_text) # Naya API call
            save_to_memory("Dipu", reply)
            asyncio.run(speak(reply))
        if not is_call_active: break

@app.route("/new_session")
def new_session():
    global current_memory_file
    current_memory_file = get_next_memory_file()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)