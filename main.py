from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()

def get_chapters(): return httpx.get("https://api.quran.com/api/v4/chapters").json()['chapters']

def get_verses(chapter, start=1, end=10):
    params = dict(fields="text_uthmani", per_page=end)
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
.header { text-align: center; padding: 30px 0; border-bottom: 1px solid var(--border); margin-bottom: 30px; }
.header h1 { font-size: 2.5rem; font-weight: 700; background: linear-gradient(90deg, var(--accent), #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 768px) { .form-grid { grid-template-columns: repeat(2, 1fr); } }
label { display: flex; align-items: center; gap: 6px; font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 6px; }
.help-btn { width: 18px; height: 18px; border-radius: 50%; border: 1px solid var(--text-secondary); background: transparent; color: var(--text-secondary); font-size: 0.75rem; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.help-btn:hover { border-color: var(--accent); color: var(--accent); }
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
.verse-badge { width: 50px; height: 50px; border: 2px solid var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; color: var(--accent); position: relative; }
.verse-badge::before { content: ''; position: absolute; width: 60px; height: 60px; border: 1px solid var(--border); border-radius: 50%; }
.verse-badge::after { content: ''; position: absolute; width: 40px; height: 40px; border: 1px solid var(--border); border-radius: 50%; }
audio { width: 100%; margin-top: 12px; border-radius: 8px; }
.step-info { font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 16px; padding: 12px 16px; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid var(--accent); }
.complete { text-align: center; padding: 60px 20px; }
.complete-icon { font-size: 4rem; margin-bottom: 16px; }
.complete-text { font-size: 1.5rem; color: var(--success); }
"""

@app.get("/", response_class=HTMLResponse)
def home():
    chapters = get_chapters()
    opts = "".join([f'<option value="{c["id"]}">{c["id"]}. {c["name_simple"]} ({c["name_arabic"]})</option>' for c in chapters])
    return f"""<!DOCTYPE html>
<html><head>
    <title>Quran Memorize</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Scheherazade+New:wght@400;700&display=swap">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>{CSS}</style>
</head><body>
    <div class="container">
        <div class="header"><h1>Quran Memorize</h1><button type="button" class="help-btn" style="margin-top:8px" onclick="showHelp('howto')">How does this app work?</button></div>
        <div class="card">
            <form hx-post="/memorize" hx-target="#session" hx-swap="innerHTML">
                <div class="form-grid">
                    <div><label>Chapter <button type="button" class="help-btn" onclick="showHelp('chapter')">?</button></label><select name="chapter">{opts}</select></div>
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
    const helpData = {
        chapter: {title: 'Chapter (Surah)', text: 'Select which chapter (Surah) of the Quran you want to memorize. The Quran has 114 chapters, each varying in length.'},
        start: {title: 'Start Verse', text: 'The verse number to begin memorizing from. Each chapter has a different number of verses (Ayat).'},
        end: {title: 'End Verse', text: 'The verse number to stop at. Select a small range (3-5 verses) for effective memorization sessions.'},
        repeats: {title: 'Repetitions', text: 'How many times each verse (and verse combination) will be repeated. Repetition is key to memorization - 3 times is a good default.'},
        howto: {title: 'How It Works', text: 'This app uses the proven memorization technique: First, each verse is repeated individually. Then verses are combined progressively (1+2, then 1+2+3, etc.) with repetitions. Audio plays automatically - just listen and recite along until the session completes.'}
    };
    function showHelp(key) { document.getElementById('help-title').textContent = helpData[key].title; document.getElementById('help-text').textContent = helpData[key].text; document.getElementById('help-popup').classList.add('active'); }
    function hideHelp() { document.getElementById('help-popup').classList.remove('active'); }
    </script>
</body></html>"""

@app.post("/memorize", response_class=HTMLResponse)
def memorize(chapter: int = Form(...), start: int = Form(...), end: int = Form(...), repeats: int = Form(...)):
    verses = get_verses(chapter, start, end)
    pattern = memorize_pattern(end - start + 1, repeats)
    pattern_data = [[([start + v - 1 for v in nums]), reps] for nums, reps in pattern]
    hidden = "".join([f'<input type="hidden" id="v{v["verse_number"]}" value="{v["text_uthmani"]}">' for v in verses.values()])
    return f"""
<h2 style="font-size:1.5rem;margin-bottom:16px">Memorizing {chapter}:{start}-{end}</h2>
<div id="current-step"><button onclick="startSession()" class="btn btn-success" style="font-size:1.5rem;padding:20px 40px">▶ Start Session</button></div>
{hidden}
<script>
const pattern = {pattern_data};
const chapter = {chapter};
let stepIdx = 0, repIdx = 0;
function startSession() {{ showStep(); }}
function showStep() {{
    if (stepIdx >= pattern.length) {{ document.getElementById('current-step').innerHTML = '<div class="complete"><div class="complete-icon">✅</div><div class="complete-text">Session Complete!</div></div>'; return; }}
    const [verses, reps] = pattern[stepIdx];
    let html = '<div class="step-info">Verses ' + verses.join(', ') + ' — Repetition ' + (repIdx+1) + ' of ' + reps + '</div>';
    verses.forEach(v => {{
        const text = document.getElementById('v' + v).value;
        const audio = 'https://verses.quran.com/Alafasy/mp3/' + String(chapter).padStart(3,'0') + String(v).padStart(3,'0') + '.mp3';
        html += '<div class="verse-card"><div class="verse-header"><div class="arabic-text">' + text + '</div><div class="verse-badge">' + v + '</div></div><audio src="' + audio + '" controls></audio></div>';
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
