<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8" />
  <title>Jamakol (Jaamakaala) Chart</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    :root{
      --border:#6b4eff;
      --text:#2b2b2b;
      --muted:#6b7280;
      --bg:#ffffff;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      background:#f5f7fb;
      font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Noto Sans Tamil',sans-serif;
      color:var(--text);
    }
    .wrap{
      width:min(720px,95vw);
      background:var(--bg);
      padding:16px;
      border-radius:16px;
      box-shadow:0 10px 30px rgba(0,0,0,.08);
    }
    .title{
      display:flex;align-items:center;justify-content:space-between;gap:12px;
      margin-bottom:10px;
    }
    .title h1{font-size:20px;margin:0}
    .controls{
      display:grid;grid-template-columns:repeat(4,1fr);gap:8px;
      margin-bottom:12px;
    }
    .controls input{
      width:100%;padding:8px 10px;border-radius:10px;border:1px solid #e5e7eb;
    }
    .chart{
      position:relative;
      width:100%;
      aspect-ratio:1/1;
      border:2px solid var(--border);
      border-radius:10px;
      display:grid;
      grid-template-columns:repeat(3,1fr);
      grid-template-rows:repeat(3,1fr);
    }
    .cell{
      border:1.5px solid var(--border);
      padding:6px;
      font-size:12px;
      line-height:1.25;
    }
    .cell textarea{
      width:100%;height:100%;border:none;resize:none;outline:none;font:inherit;color:inherit;
    }
    .center{
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      text-align:center;font-size:13px;
    }
    .center .big{font-weight:700;margin-bottom:4px}
    .center .muted{color:var(--muted)}
    .legend{
      display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px;font-size:12px
    }
    .btns{display:flex;gap:8px;margin-top:10px}
    button{
      padding:8px 12px;border-radius:10px;border:1px solid #e5e7eb;background:#fff;cursor:pointer
    }
    button.primary{background:var(--border);color:#fff;border-color:var(--border)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="title">
      <h1>ஜாமகோள் / Jaamakaala Chart</h1>
      <small class="muted">Exact timing • Degrees based</small>
    </div>

    <div class="controls">
      <input id="date" type="date" />
      <input id="time" type="time" step="60" />
      <input id="place" type="text" placeholder="Place (e.g., Chennai)" />
      <input id="note" type="text" placeholder="Note (optional)" />
    </div>

    <div class="chart">
      <!-- Row 1 -->
      <div class="cell"><textarea placeholder="வடமேற்கு (NW)
கிரகம் – degree"></textarea></div>
      <div class="cell"><textarea placeholder="வடக்கு (N)
கிரகம் – degree"></textarea></div>
      <div class="cell"><textarea placeholder="வடகிழக்கு (NE)
கிரகம் – degree"></textarea></div>
      <!-- Row 2 -->
      <div class="cell"><textarea placeholder="மேற்கு (W)
கிரகம் – degree"></textarea></div>
      <div class="cell center">
        <div class="big" id="centerDate">—</div>
        <div id="centerTime">—</div>
        <div class="muted" id="centerPlace">—</div>
        <div class="muted" id="centerNote"></div>
      </div>
      <div class="cell"><textarea placeholder="கிழக்கு (E)
கிரகம் – degree"></textarea></div>
      <!-- Row 3 -->
      <div class="cell"><textarea placeholder="தென்மேற்கு (SW)
கிரகம் – degree"></textarea></div>
      <div class="cell"><textarea placeholder="தெற்கு (S)
கிரகம் – degree"></textarea></div>
      <div class="cell"><textarea placeholder="தென்கிழக்கு (SE)
கிரகம் – degree"></textarea></div>
    </div>

    <div class="legend">
      <div>NE: Divine help</div>
      <div>E: Start / Opportunity</div>
      <div>SE: Money / Effort</div>
      <div>S: Action / Blocks</div>
      <div>SW: Karma / Loss</div>
      <div>W: Result</div>
      <div>NW: Movement</div>
      <div>N: Growth</div>
    </div>

    <div class="btns">
      <button class="primary" onclick="applyCenter()">Apply Center</button>
      <button onclick="clearAll()">Clear</button>
      <button onclick="window.print()">Print / PDF</button>
    </div>
  </div>

  <script>
    function applyCenter(){
      const d=document.getElementById('date').value;
      const t=document.getElementById('time').value;
      const p=document.getElementById('place').value||'—';
      const n=document.getElementById('note').value||'';
      document.getElementById('centerDate').textContent=d?new Date(d).toLocaleDateString('ta-IN'):'—';
      document.getElementById('centerTime').textContent=t||'—';
      document.getElementById('centerPlace').textContent=p;
      document.getElementById('centerNote').textContent=n;
    }
    function clearAll(){
      document.querySelectorAll('textarea').forEach(t=>t.value='');
      ['date','time','place','note'].forEach(id=>document.getElementById(id).value='');
      document.getElementById('centerDate').textContent='—';
      document.getElementById('centerTime').textContent='—';
      document.getElementById('centerPlace').textContent='—';
      document.getElementById('centerNote').textContent='';
    }
  </script>
</body>
</html>
