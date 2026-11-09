import os, ast, sys, shutil, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SKIP = {".git", "__pycache__", ".venv", "venv", "env", "node_modules", ".pytest_cache", ".idea", ".vscode"}
SECRET = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
lines = []
def out(s=""): lines.append(str(s))
def heading(s): out(); out("="*65); out(s); out("="*65)
def rel(p): return str(p.relative_to(ROOT))
def secret(p):
    n=p.name.lower()
    return n in SECRET or n.endswith((".pem",".key",".secret"))

files=[]
dirs=[]
for current, names, filenames in os.walk(ROOT):
    names[:]=sorted(n for n in names if n not in SKIP)
    dirs.append(Path(current))
    for name in sorted(filenames):
        p=Path(current)/name
        if not any(x in SKIP for x in p.parts): files.append(p)

heading("NEXUS AI — ПОЛНЫЙ АУДИТ")
out("Дата: "+datetime.now().isoformat(timespec="seconds"))
out("Python: "+sys.version.split()[0])
out("Файлов: "+str(len(files))+" | Папок: "+str(len(dirs)))

heading("1. СТРУКТУРА")
for p in dirs:
    depth=len(p.relative_to(ROOT).parts)
    out("  "*depth+("[ROOT] " if depth==0 else "[DIR] ")+ (ROOT.name if depth==0 else p.name))

heading("2. ФАЙЛЫ")
for p in files:
    out(("[SECRET — ПРОПУЩЕН] " if secret(p) else "[FILE] ")+rel(p)+("" if secret(p) else " | "+str(p.stat().st_size)+" bytes"))

heading("3. PYTHON")
py=[p for p in files if p.suffix==".py" and not secret(p)]
ok=0
errors=0
for p in py:
    try:
        ast.parse(p.read_text(encoding="utf-8"),filename=rel(p))
        ok+=1
        out("[OK] "+rel(p))
    except Exception as e:
        errors+=1
        out("[ERROR] "+rel(p)+" : "+str(e))
out("ИТОГО: "+str(ok)+" успешно, "+str(errors)+" ошибок")

heading("4. JAVASCRIPT")
node=shutil.which("node")
js=[p for p in files if p.suffix in {".js",".mjs",".cjs"} and not secret(p)]
if not node: out("[SKIP] Node.js не найден")
else:
    for p in js:
        r=subprocess.run([node,"--check",str(p)],capture_output=True,text=True)
        out(("[OK] " if r.returncode==0 else "[ERROR] ")+rel(p))
        if r.returncode: out((r.stderr or r.stdout)[:1500])

heading("5. HTML / INLINE JAVASCRIPT")
import re, tempfile
html=[p for p in files if p.suffix==".html"]
for p in html:
    out("[HTML] "+rel(p))
    if not node: continue
    data=p.read_text(encoding="utf-8")
    scripts=re.findall(r"<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script\s*>",data,re.I|re.S)
    for i,script in enumerate(scripts,1):
        name=None
        try:
            with tempfile.NamedTemporaryFile(mode="w",suffix=".js",encoding="utf-8",delete=False) as f:
                f.write(script); name=f.name
            r=subprocess.run([node,"--check",name],capture_output=True,text=True)
            out(("[OK] " if r.returncode==0 else "[ERROR] ")+rel(p)+" inline script #"+str(i))
            if r.returncode: out((r.stderr or r.stdout)[:1500])
        finally:
            if name and os.path.exists(name): os.unlink(name)

heading("6. ОСНОВНЫЕ ФАЙЛЫ")
important=["server.py","index.html","requirements.txt","nexus.css","core/brain.py","core/memory.py","core/load_guard.py","core/emergency_shield.py","modules/llm.py"]
for name in important:
    out(("[FOUND] " if (ROOT/name).is_file() else "[MISSING] ")+name)

heading("7. CSS / JSON")
for p in files:
    if p.suffix==".json" and not secret(p):
        try:
            import json
            json.loads(p.read_text(encoding="utf-8"))
            out("[OK JSON] "+rel(p))
        except Exception as e: out("[ERROR JSON] "+rel(p)+" : "+str(e))
for p in files:
    if p.suffix==".css": out("[CSS] "+rel(p))

heading("8. GIT")
git=shutil.which("git")
if git and (ROOT/".git").exists():
    r=subprocess.run([git,"-C",str(ROOT),"status","--short"],capture_output=True,text=True)
    out(r.stdout.strip() or "Рабочее дерево чистое.")
else: out("[INFO] Git не найден")

heading("9. ИТОГ")
out("Всего файлов: "+str(len(files)))
out("Python-файлов: "+str(len(py)))
out("HTML-файлов: "+str(len(html)))
out("Папок: "+str(len(dirs)))
out("Ошибок Python: "+str(errors))
out("Содержимое секретов не читалось и не выводилось.")
out("Исходные файлы не изменялись.")
out("КОНЕЦ ОТЧЁТА")

(ROOT/"PROJECT_AUDIT.txt").write_text("\n".join(lines),encoding="utf-8")
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("Отчёт: PROJECT_AUDIT.txt")
print("Файлов:",len(files),"Папок:",len(dirs),"Ошибок Python:",errors)
