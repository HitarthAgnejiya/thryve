from datetime import datetime, timezone
from html import escape
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="THRYVE — RoadGuard AI",
    description="Vercel-compatible road hazard reporting prototype.",
    version="1.0.0",
)

# Demo-only storage: serverless instances can restart and do not share this list.
reports = [
    {
        "id": "RG-1042",
        "reported_at": "2026-10-20 09:42 UTC",
        "area": "Sample Road, Demo City",
        "lat": 23.0225,
        "lon": 72.5714,
        "severity": "High",
        "status": "Needs review",
        "notes": "Illustrative demo record; verify on site.",
    },
    {
        "id": "RG-1041",
        "reported_at": "2026-10-20 08:17 UTC",
        "area": "Market Street, Demo City",
        "lat": 23.0300,
        "lon": 72.5800,
        "severity": "Medium",
        "status": "Under review",
        "notes": "Illustrative demo record; verify on site.",
    },
    {
        "id": "RG-1038",
        "reported_at": "2026-10-19 18:04 UTC",
        "area": "Ring Road, Demo City",
        "lat": 23.0100,
        "lon": 72.5600,
        "severity": "Low",
        "status": "Verified",
        "notes": "Illustrative demo record; verify on site.",
    },
]


class HazardReport(BaseModel):
    area: str = Field(min_length=2, max_length=180)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    severity: Literal["High", "Medium", "Low", "Unassessed"] = "Unassessed"
    notes: str = Field(default="", max_length=2000)


def render_rows():
    rows = []
    for item in sorted(reports, key=lambda x: x["reported_at"], reverse=True):
        rows.append(
            "<tr>"
            f"<td>{escape(item['id'])}</td>"
            f"<td>{escape(item['area'])}</td>"
            f"<td><span class='pill'>{escape(item['severity'])}</span></td>"
            f"<td>{escape(item['status'])}</td>"
            f"<td>{item['lat']:.5f}, {item['lon']:.5f}</td>"
            "</tr>"
        )
    return "\n".join(rows)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    high = sum(1 for r in reports if r["severity"] == "High")
    pending = sum(1 for r in reports if r["status"] in ("Needs review", "Under review"))
    verified = sum(1 for r in reports if r["status"] == "Verified")
    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0a1423">
<title>THRYVE | RoadGuard AI</title>
<style>
:root{color-scheme:dark;--bg:#07101c;--panel:#102035;--line:#263b53;--muted:#a9bdd4;--lime:#c5f36a}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 Inter,ui-sans-serif,system-ui,sans-serif;background:radial-gradient(ellipse at 10% 0%,#1c3550 0%,var(--bg) 55%);color:#eef5ff}
main{max-width:1120px;margin:auto;padding:32px 20px 60px}.brand{color:var(--lime);font-weight:800;letter-spacing:.12em;font-size:.82rem}
h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.08;max-width:760px;margin:18px 0}p{color:var(--muted)}.notice{padding:12px 16px;border:1px solid #665a30;background:#2b2819;border-radius:12px;color:#ffe7a0;margin:24px 0}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:24px 0}.card,.panel{background:linear-gradient(145deg,#14263b,#0e1b2d);border:1px solid var(--line);border-radius:16px;padding:20px}.label{font-size:.9rem;color:var(--muted)}.value{font-size:2rem;font-weight:750;color:var(--lime);margin-top:4px}
.panel{margin-top:18px}h2{margin-top:0}table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{text-align:left;padding:12px 10px;border-bottom:1px solid var(--line)}th{color:var(--muted)}.table-wrap{overflow-x:auto}.pill{display:inline-block;border:1px solid #40566e;border-radius:999px;padding:3px 9px}
form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}label{display:grid;gap:6px;color:var(--muted)}input,select,textarea{width:100%;padding:11px;border:1px solid #3a5068;border-radius:9px;background:#091525;color:#fff;font:inherit}textarea{min-height:85px}button{border:0;border-radius:9px;padding:12px 16px;background:var(--lime);color:#14200a;font-weight:800;cursor:pointer}form button{align-self:end}#result{grid-column:1/-1}.wide{grid-column:1/-1}a{color:var(--lime)}footer{margin-top:24px;color:var(--muted);font-size:.85rem}
@media(max-width:700px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}form{grid-template-columns:1fr}.wide{grid-column:auto}th,td{white-space:nowrap}}
</style></head>
<body><main>
<div class="brand">THRYVE / ROADGUARD AI</div>
<h1>Spot the damage. <span style="color:var(--lime)">Prioritise the repair.</span></h1>
<p>Report road hazards, review severity, and keep road-distress information in one simple dashboard.</p>
<div class="notice">Prototype only. Demo records are illustrative. Verify locations and severity with a human reviewer before taking action.</div>
<section class="metrics">
<div class="card"><div class="label">Road reports</div><div class="value" id="total">TOTAL</div></div>
<div class="card"><div class="label">High priority</div><div class="value" id="high">HIGH</div></div>
<div class="card"><div class="label">Awaiting review</div><div class="value" id="pending">PENDING</div></div>
<div class="card"><div class="label">Verified</div><div class="value" id="verified">VERIFIED</div></div>
</section>
<section class="panel"><h2>Report a road hazard</h2>
<form id="report-form">
<label>Road / area<input name="area" required minlength="2" maxlength="180" placeholder="Street name or landmark"></label>
<label>Estimated severity<select name="severity"><option>Unassessed</option><option>High</option><option>Medium</option><option>Low</option></select></label>
<label>Latitude<input name="lat" type="number" min="-90" max="90" step="any" value="23.0225" required></label>
<label>Longitude<input name="lon" type="number" min="-180" max="180" step="any" value="72.5714" required></label>
<label class="wide">Notes<textarea name="notes" maxlength="2000" placeholder="Describe the visible road issue"></textarea></label>
<button type="submit">Submit report</button><div id="result" role="status"></div>
</form></section>
<section class="panel"><h2>Latest reports</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Road / area</th><th>Severity</th><th>Status</th><th>Coordinates</th></tr></thead><tbody id="rows"></tbody></table></div>
<p><a href="/docs">API documentation</a> · <a href="/api/reports">View reports JSON</a></p></section>
<footer>ROADGUARD AI · Vercel-compatible demo. Reports use temporary in-memory storage; add a database for persistent production data.</footer>
</main>
<script>
async function refresh(){
 const res=await fetch('/api/reports'); const data=await res.json();
 document.querySelector('#total').textContent=data.length;
 document.querySelector('#high').textContent=data.filter(x=>x.severity==='High').length;
 document.querySelector('#pending').textContent=data.filter(x=>['Needs review','Under review'].includes(x.status)).length;
 document.querySelector('#verified').textContent=data.filter(x=>x.status==='Verified').length;
 document.querySelector('#rows').innerHTML=data.map(x=>'<tr><td>'+esc(x.id)+'</td><td>'+esc(x.area)+'</td><td><span class="pill">'+esc(x.severity)+'</span></td><td>'+esc(x.status)+'</td><td>'+Number(x.lat).toFixed(5)+', '+Number(x.lon).toFixed(5)+'</td></tr>').join('');
}
function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
document.querySelector('#report-form').addEventListener('submit',async e=>{
 e.preventDefault();const form=e.currentTarget;const d=Object.fromEntries(new FormData(form).entries());
 d.lat=Number(d.lat);d.lon=Number(d.lon);
 const result=document.querySelector('#result');result.textContent='Submitting…';
 try{const r=await fetch('/api/reports',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});const body=await r.json();
 if(!r.ok)throw new Error(body.detail||'Could not submit report');
 result.textContent='Report submitted for review.';form.reset();await refresh();
 }catch(err){result.textContent=err.message;}
});
refresh();
</script></body></html>"""
    page = page.replace('id="total">TOTAL', f'id="total">{len(reports)}')
    page = page.replace('id="high">HIGH', f'id="high">{high}')
    page = page.replace('id="pending">PENDING', f'id="pending">{pending}')
    page = page.replace('id="verified">VERIFIED', f'id="verified">{verified}')
    page = page.replace('<tbody id="rows"></tbody>', f'<tbody id="rows">{render_rows()}</tbody>')
    return HTMLResponse(page)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "RoadGuard AI"}


@app.get("/api/reports")
async def list_reports():
    return reports


@app.post("/api/reports", status_code=201)
async def create_report(report: HazardReport):
    area = report.area.strip()
    if not area:
        raise HTTPException(status_code=422, detail="Road / area is required.")
    item = {
        "id": f"RG-{uuid4().hex[:6].upper()}",
        "reported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "area": area,
        "lat": report.lat,
        "lon": report.lon,
        "severity": report.severity,
        "status": "Needs review",
        "notes": report.notes.strip(),
    }
    reports.append(item)
    return item
