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

@app.get("/", response_class=HTMLResponse)
def home():
    chapters = get_chapters()
    opts = "".join([f'<option value="{c["id"]}">{c["id"]}. {c["name_simple"]}</option>' for c in chapters])
    return f"""<!DOCTYPE html>
<html><head>
    <title>Quran Memorize</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Scheherazade+New:wght@400;700&display=swap">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head><body class="min-h-screen bg-gray-100">
    <div class="max-w-4xl mx-auto p-4">
        <h1 class="text-4xl font-bold text-center my-8">Quran Memorize</h1>
        <div class="bg-white p-6 rounded-lg shadow mb-6">
            <form hx-post="/memorize" hx-target="#session" hx-swap="innerHTML">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div><label class="block mb-1">Chapter</label><select name="chapter" class="w-full p-2 border rounded">{opts}</select></div>
                    <div><label class="block mb-1">Start Verse</label><input type="number" name="start" value="1" min="1" class="w-full p-2 border rounded"></div>
                    <div><label class="block mb-1">End Verse</label><input type="number" name="end" value="5" min="1" class="w-full p-2 border rounded"></div>
                    <div><label class="block mb-1">Repeats</label><input type="number" name="repeats" value="3" min="1" max="10" class="w-full p-2 border rounded"></div>
                </div>
                <button type="submit" class="mt-4 w-full bg-blue-600 text-white py-3 rounded-lg text-lg hover:bg-blue-700">Start Memorizing</button>
            </form>
        </div>
        <div id="session"></div>
    </div>
</body></html>"""

@app.post("/memorize", response_class=HTMLResponse)
def memorize(chapter: int = Form(...), start: int = Form(...), end: int = Form(...), repeats: int = Form(...)):
    verses = get_verses(chapter, start, end)
    pattern = memorize_pattern(end - start + 1, repeats)
    pattern_data = [([start + v - 1 for v in nums], reps) for nums, reps in pattern]
    hidden = "".join([f'<input type="hidden" id="v{v["verse_number"]}" value="{v["text_uthmani"]}">' for v in verses.values()])
    return f"""
<h2 class="text-2xl font-bold mb-4">Memorizing {chapter}:{start}-{end}</h2>
<div id="current-step"></div>
{hidden}
<script>
const pattern = {pattern_data};
const chapter = {chapter};
let stepIdx = 0, repIdx = 0;
function showStep() {{
    if (stepIdx >= pattern.length) {{ document.getElementById('current-step').innerHTML = '<div class="text-2xl text-center p-8">✅ Session Complete!</div>'; return; }}
    const [verses, reps] = pattern[stepIdx];
    let html = '<div class="mb-4 text-lg font-semibold">Verses ' + verses.join(', ') + ' — Rep ' + (repIdx+1) + '/' + reps + '</div>';
    verses.forEach(v => {{
        const text = document.getElementById('v' + v).value;
        const audio = 'https://verses.quran.com/7/' + String(chapter).padStart(3,'0') + String(v).padStart(3,'0') + '.mp3';
        html += '<div class="bg-white rounded-lg p-6 mb-4 shadow"><div class="text-3xl text-right" dir="rtl" style="font-family: Scheherazade New; line-height:2">' + text + '</div><div class="text-sm text-gray-500 mt-2">' + chapter + ':' + v + '</div><audio src="' + audio + '" controls class="w-full mt-2"></audio></div>';
    }});
    html += '<button onclick="nextRep()" class="w-full mt-4 bg-green-600 text-white py-3 rounded-lg text-lg hover:bg-green-700">Next →</button>';
    document.getElementById('current-step').innerHTML = html;
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
