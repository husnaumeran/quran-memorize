from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI()

MANIFEST = {
    "name": "Quran Memorize",
    "short_name": "QuranMemo",
    "description": "Memorize the Quran with proven repetition techniques",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0d1117",
    "theme_color": "#2f81f7",
    "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
    ]
}

@app.get("/ads.txt")
def ads_txt():
    return "google.com, pub-1408773845403605, DIRECT, f08c47fec0942fa0"

@app.get("/manifest.json")
def manifest(): return JSONResponse(MANIFEST)

@app.get("/sw.js")
def service_worker():
    return HTMLResponse(content="self.addEventListener('fetch', e => e.respondWith(fetch(e.request)));", media_type="application/javascript")

@app.get("/icon-192.png")
@app.get("/icon-512.png")
def icon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="#2f81f7" width="100" height="100" rx="20"/><text x="50" y="65" font-size="50" text-anchor="middle" fill="white">📖</text></svg>'
    return HTMLResponse(content=svg, media_type="image/svg+xml")

def get_chapters(): return httpx.get("https://api.quran.com/api/v4/chapters").json()['chapters']

TRANSLATIONS = {
    "english": [
        (20, "Saheeh International (Popular)"),
        (85, "Abdul Haleem (Modern)"),
        (22, "Yusuf Ali (Classic)"),
        (84, "Mufti Taqi Usmani"),
        (95, "Maududi (Tafhim)"),
        (19, "Pickthall"),
        (149, "Bridges (Fadel Soliman)"),
        (203, "Al-Hilali & Khan"),
        (57, "Transliteration"),
    ],
    "urdu": [
        (97, "Ahmed Ali"),
        (158, "Fateh Muhammad Jalandhry"),
        (234, "Maulana Junagarhi"),
        (54, "Maududi (Tafheem ul Quran)"),
    ],
    "french": [
        (31, "Muhammad Hamidullah"),
        (136, "Rashid Maash"),
    ],
    "spanish": [
        (83, "Julio Cortes"),
        (140, "Muhammad Isa Garcia"),
    ],
    "turkish": [
        (52, "Diyanet Isleri"),
        (124, "Elmalili Hamdi Yazir"),
    ],
    "indonesian": [
        (33, "Indonesian Ministry of Religious Affairs"),
        (134, "Tafsir Jalalayn"),
    ],
    "bengali": [
        (161, "Muhiuddin Khan"),
        (163, "Taisirul Quran"),
    ],
    "hindi": [
        (122, "Suhel Farooq Khan / Saifur Rahman Nadwi"),
    ],
    "malay": [
        (39, "Abdullah Basmeih"),
    ],
    "russian": [
        (45, "Elmir Kuliev"),
        (79, "Abu Adel"),
    ],
    "german": [
        (27, "Abu Rida Muhammad ibn Ahmad ibn Rassoul"),
        (208, "Bubenheim & Elyas"),
    ],
    "chinese": [
        (56, "Ma Jian"),
    ],
}

RECITERS = [
    (7, "Mishari Rashid al-Afasy"),
    (2, "AbdulBaset AbdulSamad (Murattal)"),
    (1, "AbdulBaset AbdulSamad (Mujawwad)"),
    (3, "Abdur-Rahman as-Sudais"),
    (4, "Abu Bakr al-Shatri"),
    (5, "Hani ar-Rifai"),
    (6, "Mahmoud Khalil Al-Husary"),
    (12, "Mahmoud Khalil Al-Husary (Muallim)"),
    (9, "Mohamed Siddiq al-Minshawi (Murattal)"),
    (8, "Mohamed Siddiq al-Minshawi (Mujawwad)"),
    (10, "Sa`ud ash-Shuraym"),
    (11, "Mohamed al-Tablawi"),
]

def get_audio_urls(reciter_id, chapter, verses):
    """Get audio URLs for verses from API"""
    verse_keys = [f"{chapter}:{v}" for v in verses]
    urls = {}
    for vk in verse_keys:
        r = httpx.get(f"https://api.quran.com/api/v4/recitations/{reciter_id}/by_ayah/{vk}")
        data = r.json()
        if data['audio_files']:
            urls[vk] = "https://verses.quran.com/" + data['audio_files'][0]['url']
    return urls

def get_verses(chapter, start=1, end=10, translation_id=None):
    params = dict(fields="text_uthmani", per_page=end)
    if translation_id:
        params['translations'] = translation_id
    r = httpx.get(f"https://api.quran.com/api/v4/verses/by_chapter/{chapter}", params=params).json()
    return {v['verse_number']: v for v in r['verses'] if v['verse_number'] >= start and v['verse_number'] <= end}

def memorize_pattern(n_verses, repeats=3):
    pattern = []
    for i in range(1, n_verses+1):
        pattern.append(([i], repeats))
        if i > 1: pattern.append((list(range(1, i+1)), repeats))
    return pattern

CSS = """
:root { --bg-primary: #0d1117; --bg-secondary: #161b22; --bg-card: #1c2128; --text-primary: #e6edf3; --text-secondary: #8b949e; --accent: #2f81f7; --accent-hover: #388bfd; --border: #30363d; --success: #238636; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-primary); color: var(--text-primary); min-height: 100vh; }
.container { max-width: 900px; margin: 0 auto; padding: 20px; }
.header { text-align: center; padding: 30px 0; border-bottom: 1px solid var(--border); margin-bottom: 30px; display: flex; flex-direction: column; align-items: center; gap: 8px; position: relative; }
.hamburger { position: absolute; right: 0; top: 30px; background: transparent; border: none; cursor: pointer; padding: 8px; }
.hamburger span { display: block; width: 24px; height: 3px; background: var(--text-primary); margin: 5px 0; border-radius: 2px; transition: 0.3s; }
.nav-menu { display: none; position: absolute; right: 0; top: 70px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; min-width: 180px; z-index: 50; overflow: hidden; }
.nav-menu.active { display: block; }
.nav-menu a { display: block; padding: 12px 16px; color: var(--text-primary); text-decoration: none; border-bottom: 1px solid var(--border); }
.nav-menu a:last-child { border-bottom: none; }
.nav-menu a:hover { background: var(--bg-secondary); color: var(--accent); }
.header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(90deg, var(--accent), #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 768px) { .form-grid { grid-template-columns: repeat(2, 1fr); } }
label { display: flex; align-items: center; gap: 6px; font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 6px; }
.help-btn { width: 18px; height: 18px; border-radius: 50%; border: 1px solid var(--text-secondary); background: transparent; color: var(--text-secondary); font-size: 0.75rem; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.help-btn:hover { border-color: var(--accent); color: var(--accent); }
.help-link { background: transparent; border: none; color: var(--text-secondary); font-size: 0.875rem; cursor: pointer; text-decoration: underline; white-space: nowrap; }
.help-link:hover { color: var(--accent); }
.donate-banner { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 10px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 20px; font-size: 0.875rem; color: var(--text-secondary); }
.donate-btn { background: #ffdd00; color: #000; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.8rem; }
.donate-btn:hover { background: #e6c700; }
.ad-space { text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.75rem; }
.ad-space a { color: var(--accent); }
.help-popup { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 100; align-items: center; justify-content: center; }
.help-popup.active { display: flex; }
.help-content { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; max-width: 500px; margin: 20px; }
.help-content h3 { color: var(--accent); margin-bottom: 12px; }
.help-content p { color: var(--text-secondary); line-height: 1.6; }
.help-content button { margin-top: 16px; padding: 8px 16px; }
select, input { width: 100%; padding: 10px 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 1rem; }
select:focus, input:focus { outline: none; border-color: var(--accent); }
.btn { width: 100%; padding: 14px; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: all 0.2s; margin-top: 20px; }
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-success { background: var(--success); color: white; }
.btn-success:hover { background: #2ea043; }
.verse-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 16px; display: flex; flex-direction: column; align-items: center; }
.verse-header { display: flex; align-items: center; justify-content: flex-end; width: 100%; gap: 16px; direction: rtl; }
.arabic-text { font-family: 'Scheherazade New', 'Traditional Arabic', serif; font-size: 2.5rem; line-height: 2; color: var(--text-primary); }
.trans-text { font-size: 1rem; color: var(--text-secondary); margin: 12px 0; text-align: center; line-height: 1.6; }
.verse-badge { width: 50px; height: 50px; border: 2px solid var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: var(--accent); position: relative; }
.verse-badge::before { content: ''; position: absolute; width: 60px; height: 60px; border: 1px solid var(--border); border-radius: 50%; }
.verse-badge::after { content: ''; position: absolute; width: 40px; height: 40px; border: 1px solid var(--border); border-radius: 50%; }
audio { width: 100%; margin-top: 12px; border-radius: 8px; }
.step-info { font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 16px; padding: 12px 16px; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid var(--accent); }
.complete { text-align: center; padding: 60px 20px; }
.complete-icon { font-size: 4rem; margin-bottom: 16px; }
.complete-text { font-size: 1.5rem; color: var(--success); }
"""

@app.get("/about", response_class=HTMLResponse)
def about():
    return f"""<!DOCTYPE html>
<html><head>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1408773845403605" crossorigin="anonymous"></script>
    <title>About - Quran Memorize</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#2f81f7">
    <link rel="manifest" href="/manifest.json">
    <style>{CSS}</style>
</head><body>
    <div class="container">
        <div class="header"><h1>About Quran Memorize</h1></div>
        <div class="card">
            <h3 style="color: var(--accent); margin-bottom: 16px;">Our Mission</h3>
            <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px;">
                Quran Memorize is a free tool designed to help Muslims memorize the Holy Quran using proven repetition techniques. 
                Our app plays verses and their combinations multiple times, making it easier to commit them to memory.
            </p>
            <h3 style="color: var(--accent); margin-bottom: 16px;">Features</h3>
            <ul style="color: var(--text-secondary); line-height: 2; padding-left: 20px;">
                <li>Progressive repetition pattern for effective memorization</li>
                <li>Audio from renowned reciter Sheikh Mishary Alafasy</li>
                <li>Works offline as a PWA (installable app)</li>
                <li>Free and open for everyone</li>
            </ul>
        </div>
        <div class="card">
            <h3 style="color: var(--accent); margin-bottom: 16px;">Contact</h3>
            <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 10px;">📧 <strong>Feedback & Suggestions:</strong> <a href="mailto:husna.umeran.1007@gmail.com?subject=Feedback for Quran Memorize" style="color: var(--accent);">husna.umeran.1007@gmail.com</a></p>
            <p style="color: var(--text-secondary); line-height: 1.8;">📢 <strong>Advertising Inquiries:</strong> <a href="mailto:husna.umeran.1007@gmail.com?subject=Advertising on Quran Memorize" style="color: var(--accent);">husna.umeran.1007@gmail.com</a></p>
        </div>
        <div class="card" style="text-align: center;">
            <a href="/" class="btn btn-primary" style="display: inline-block; width: auto; padding: 12px 32px; text-decoration: none;">← Back to App</a>
        </div>
    </div>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    chapters = get_chapters()
    opts = "".join([f'<option value="{c["id"]}">{c["id"]}. {c["name_simple"]} ({c["name_arabic"]})</option>' for c in chapters])
    reciter_opts = "".join([f'<option value="{rid}">{name}</option>' for rid, name in RECITERS])
    import json
    lang_opts = '<option value="">No Translation</option>' + "".join([f'<option value="{lang}">{lang.title()}</option>' for lang in TRANSLATIONS.keys()])
    translations_json = json.dumps(TRANSLATIONS)
    return f"""<!DOCTYPE html>
<html><head>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1408773845403605" crossorigin="anonymous"></script>
    <title>Quran Memorize</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#2f81f7">
    <meta name="description" content="Memorize the Quran with proven repetition techniques">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192.png">
    <script>if('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');</script>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Scheherazade+New:wght@400;700&display=swap">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script>var pattern = [], chapter = 1, stepIdx = 0, repIdx = 0;</script>
    <style>{CSS}</style>
</head><body>
    <div class="container">
        <div class="header">
            <h1>Quran Memorize</h1>
            <button class="hamburger" onclick="toggleMenu()"><span></span><span></span><span></span></button>
            <nav class="nav-menu" id="navMenu">
                <a href="#" onclick="showHelp(\'howto\'); toggleMenu();">How It Works</a>
                <a href="/about">About</a>
            </nav>
        </div>
        <div class="donate-banner"><span>☕ Enjoying this free app?</span><a href="https://buymeacoffee.com/husnau" target="_blank" class="donate-btn">Support the Developer</a></div>
        <div class="card">
            <form hx-post="/memorize" hx-target="#session" hx-swap="innerHTML">
                <div class="form-grid">
                    <div><label>Chapter <button type="button" class="help-btn" onclick="showHelp('chapter')">?</button></label><select name="chapter">{opts}</select></div>
                    <div><label>Reciter <button type="button" class="help-btn" onclick="showHelp('reciter')">?</button></label><select name="reciter">{reciter_opts}</select></div>
                    <div><label>Language <button type="button" class="help-btn" onclick="showHelp('translation')">?</button></label><select name="language" onchange="updateTranslations(this.value)">{lang_opts}</select></div>
                    <div><label>Translation</label><select name="translation" id="translationSelect"><option value="">Select language first</option></select></div>
                    <div><label>Start Verse <button type="button" class="help-btn" onclick="showHelp('start')">?</button></label><input type="number" name="start" value="1" min="1"></div>
                    <div><label>End Verse <button type="button" class="help-btn" onclick="showHelp('end')">?</button></label><input type="number" name="end" value="5" min="1"></div>
                    <div><label>Repeats <button type="button" class="help-btn" onclick="showHelp('repeats')">?</button></label><input type="number" name="repeats" value="3" min="1" max="10"></div>
                </div>
                <button type="submit" class="btn btn-primary">Start Memorizing</button>
            </form>
        </div>
        <div id="session"></div>
    </div>
    <div id="help-popup" class="help-popup" onclick="hideHelp()">
        <div class="help-content" onclick="event.stopPropagation()">
            <h3 id="help-title"></h3>
            <p id="help-text"></p>
            <button class="btn btn-primary" onclick="hideHelp()">Got it</button>
        </div>
    </div>
    <script>
    const helpData = {{
        chapter: {{title: 'Chapter (Surah)', text: 'Select which chapter (Surah) of the Quran you want to memorize. The Quran has 114 chapters, each varying in length.'}},
        reciter: {{title: 'Reciter (Qari)', text: 'Choose your preferred Quran reciter. Different reciters have different styles - Murattal is a slower, teaching-pace style while Mujawwad is more melodious.'}},
        translation: {{title: 'Translation', text: 'Show an English translation below each verse. Select Transliteration for pronunciation help in Latin letters.'}},
        start: {{title: 'Start Verse', text: 'The verse number to begin memorizing from. Each chapter has a different number of verses (Ayat).'}},
        end: {{title: 'End Verse', text: 'The verse number to stop at. Select a small range (3-5 verses) for effective memorization sessions.'}},
        repeats: {{title: 'Repetitions', text: 'How many times each verse (and verse combination) will be repeated. Repetition is key to memorization - 3 times is a good default.'}},
        howto: {{title: 'How It Works', text: '<ul style="text-align:left;margin:0;padding-left:20px"><li>Each verse is repeated individually first</li><li>Verses are then combined progressively (1+2, then 1+2+3, etc.)</li><li>Each combination is repeated multiple times</li><li>Audio plays automatically - just listen and recite along</li></ul>'}}
    }};
    function showHelp(key) {{ document.getElementById('help-title').textContent = helpData[key].title; document.getElementById('help-text').innerHTML = helpData[key].text; document.getElementById('help-popup').classList.add('active'); }}
    function hideHelp() {{ document.getElementById('help-popup').classList.remove('active'); }}
    function toggleMenu() {{ document.getElementById('navMenu').classList.toggle('active'); }}
    const translationsData = {translations_json};
    function updateTranslations(lang) {{
        const select = document.getElementById('translationSelect');
        select.innerHTML = '<option value="">No Translation</option>';
        if (lang && translationsData[lang]) {{
            translationsData[lang].forEach(([id, name]) => {{
                select.innerHTML += `<option value="${{id}}">${{name}}</option>`;
            }});
        }}
    }}
    document.addEventListener('click', function(e) {{ if (!e.target.closest('.hamburger') && !e.target.closest('.nav-menu')) document.getElementById('navMenu').classList.remove('active'); }});
    </script>
</body></html>"""

@app.post("/memorize", response_class=HTMLResponse)
def memorize(chapter: int = Form(...), reciter: int = Form(...), translation: str = Form(""), start: int = Form(...), end: int = Form(...), repeats: int = Form(...)):
    trans_id = int(translation) if translation else None
    verses = get_verses(chapter, start, end, trans_id)
    audio_urls = get_audio_urls(reciter, chapter, list(verses.keys()))
    pattern = memorize_pattern(end - start + 1, repeats)
    pattern_data = [[([start + v - 1 for v in nums]), reps] for nums, reps in pattern]
    hidden = "".join([f'<input type="hidden" id="v{v["verse_number"]}" value="{v["text_uthmani"]}">' for v in verses.values()])
    # Store translations
    trans_hidden = ""
    if trans_id:
        for v in verses.values():
            trans_text = v.get('translations', [{}])[0].get('text', '') if v.get('translations') else ''
            trans_hidden += f'<input type="hidden" id="t{v["verse_number"]}" value="{trans_text}">'
    audio_hidden = "".join([f'<input type="hidden" id="a{vk.split(":")[1]}" value="{url}">' for vk, url in audio_urls.items()])
    return f"""
<h2 style="font-size:1.5rem;margin-bottom:16px">Memorizing {chapter}:{start}-{end}</h2>
<div id="current-step"><button onclick="startSession()" class="btn btn-success" style="font-size:1.5rem;padding:20px 40px">▶ Start Session</button></div>
{hidden}
{trans_hidden}
{audio_hidden}
<script>
pattern = {pattern_data};
chapter = {chapter};
stepIdx = 0; repIdx = 0;
function startSession() {{ stepIdx = 0; repIdx = 0; showStep(); }}
function showStep() {{
    if (stepIdx >= pattern.length) {{ document.getElementById('current-step').innerHTML = '<div class="complete"><div class="complete-icon">✅</div><div class="complete-text">Session Complete!</div></div>'; return; }}
    const [verses, reps] = pattern[stepIdx];
    let html = '<div class="step-info">Verses ' + verses.join(', ') + ' — Repetition ' + (repIdx+1) + ' of ' + reps + '</div>';
    verses.forEach(v => {{
        const text = document.getElementById('v' + v).value;
        const audio = document.getElementById('a' + v).value;
        const transEl = document.getElementById('t' + v);
        const trans = transEl ? transEl.value : '';
        const transHtml = trans ? '<div class="trans-text">' + trans + '</div>' : '';
        html += '<div class="verse-card"><div class="verse-header"><div class="arabic-text">' + text + '</div><div class="verse-badge">' + v + '</div></div>' + transHtml + '<audio src="' + audio + '" controls></audio></div>';
    }});
    html += '<button onclick="nextRep()" class="btn btn-success">Next →</button>';
    document.getElementById('current-step').innerHTML = html;
    const audios = document.getElementById('current-step').querySelectorAll('audio');
    if (audios.length > 0) {{
        let idx = 0;
        const playNext = () => {{ if (++idx < audios.length) {{ audios[idx].play(); audios[idx].onended = playNext; }} else {{ nextRep(); }} }};
        audios[0].onended = playNext;
        audios[0].play().catch(e => console.log('Autoplay blocked:', e));
    }}
}}
function nextRep() {{
    repIdx++;
    if (repIdx >= pattern[stepIdx][1]) {{ stepIdx++; repIdx = 0; }}
    showStep();
}}
showStep();
</script>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
