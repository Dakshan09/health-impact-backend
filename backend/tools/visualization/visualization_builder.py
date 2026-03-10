"""
Visualization HTML Builder
Generates a premium dark-themed interactive health report matching the sample design.
"""
import json as _json
from datetime import datetime


# Disease label mapping from internal category keys
DISEASE_MAP = {
    "cardiovascular": "Cardiovascular Disease",
    "metabolic": "Metabolic Syndrome",
    "mental_health": "Mental Health",
    "respiratory": "Respiratory Disease",
    "musculoskeletal": "Musculoskeletal Health",
}

CHART_COLORS = ["#6366F1", "#EC4899", "#10B981", "#F59E0B", "#3B82F6"]


def build_visualization_html(
    patient_name: str,
    patient_data: dict,
    risk_categories: dict,
    lifestyle_scores: dict,
    overall_risk: str,
    analysis: str,
) -> str:
    """
    Build a premium dark-themed visualization HTML matching the sample design.
    Features: Chart.js trend lines + radar chart, health score, food swaps, action plan.
    """
    date_str = datetime.now().strftime("%B %d, %Y")

    # ── Disease risk objects ─────────────────────────────────────────────────
    diseases = []
    for i, (key, score) in enumerate(risk_categories.items()):
        label = DISEASE_MAP.get(key, key.replace("_", " ").title())
        current = int(score)
        proj_5yr = int(score)
        proj_10yr = min(int(score) + 10, 100)
        proj_20yr = min(int(score) * 2, 100)
        diseases.append({
            "key": key,
            "label": label,
            "score": current,
            "proj_5yr": proj_5yr,
            "proj_10yr": proj_10yr,
            "proj_20yr": proj_20yr,
            "color": CHART_COLORS[i % len(CHART_COLORS)],
        })

    # ── Health score + overall label ─────────────────────────────────────────
    avg_risk = sum(risk_categories.values()) / max(len(risk_categories), 1)
    health_score = max(10, int(100 - avg_risk))
    risk_label_text = {
        "High": "High Risk Profile",
        "Moderate": "Moderate Risk Profile",
        "Low": "Low Risk Profile",
    }.get(overall_risk, "Unknown Risk Profile")
    risk_label_color = {
        "High": "var(--danger)",
        "Moderate": "var(--warning)",
        "Low": "var(--success)",
    }.get(overall_risk, "var(--text-muted)")

    # ── Top concerns pills ────────────────────────────────────────────────────
    concerns = sorted(diseases, key=lambda d: d["score"], reverse=True)[:3]
    concern_pills = "".join(
        f'<span class="pill critical">{d["label"]}</span>' for d in concerns
    )

    # ── Disease risk cards ────────────────────────────────────────────────────
    disease_cards_html = ""
    for d in diseases:
        css_risk = "risk-high" if d["score"] >= 70 else ("risk-moderate" if d["score"] >= 40 else "risk-low")
        disease_cards_html += f"""
        <div class="card">
            <div class="card-header">
                <h2>{d["label"]}</h2>
                <span class="metric-value {css_risk}">{d["score"]}%</span>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; flex-grow: 1;">
                Risk factors detected based on health markers.
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 8px;">
                <div class="detail-row" style="padding: 0.4rem 0; border: none;">
                    <span style="font-size: 0.8rem; color: var(--text-muted);">10-Year Projection</span>
                    <span style="font-weight: 600;">{d["proj_10yr"]}%</span>
                </div>
            </div>
        </div>
        """

    # ── Nutritional status ────────────────────────────────────────────────────
    diet_score = lifestyle_scores.get("diet", 0)

    # Build deficiency pills from low-scoring lifestyle areas
    deficiency_pills = ""
    strength_pills = ""
    for k, v in lifestyle_scores.items():
        label = k.replace("_", " ").title()
        if v < 50:
            deficiency_pills += f'<span class="pill warning">{label}</span>'
        elif v >= 70:
            strength_pills += f'<span class="pill good">{label}</span>'

    # ── Food swaps ────────────────────────────────────────────────────────────
    sugar = patient_data.get("sugarConsumption", "").lower()
    processed = patient_data.get("processedFoodConsumption", "").lower()

    food_swaps = [
        ("White bread/rice", "Whole wheat bread / brown rice", ""),
        ("Sugary snacks", "Mixed nuts, fruits, dark chocolate", ""),
        ("Soda / sweetened drinks", "Water, herbal tea, lemon water", ""),
        ("Fried foods", "Grilled, steamed, or baked alternatives", ""),
    ]
    if "high" in sugar or "very high" in sugar:
        food_swaps[1] = ("Refined sugars & sweets", "Natural sweeteners (dates, honey)", "Reduces blood glucose spikes by 30-40%")
    if "high" in processed or "very high" in processed:
        food_swaps[3] = ("Ultra-processed foods", "Whole, minimally processed alternatives", "Reduces inflammation markers")

    swaps_html = ""
    for old, new, reason in food_swaps:
        swaps_html += f"""
        <div class="swap-item">
            <div class="swap-old">{old}</div>
            <div class="swap-arrow">➔</div>
            <div class="swap-new">{new}</div>
            <div class="swap-reason">{reason}</div>
        </div>
        """

    # ── Action plan from AI analysis ──────────────────────────────────────────
    action_items = []
    for line in analysis.split("\n"):
        s = line.strip()
        if (s.startswith("- ") or s.startswith("* ") or s.startswith("• ")):
            text = s[2:].strip()
            if len(text) > 15 and len(action_items) < 6:
                priority = "HIGH" if any(
                    w in text.lower() for w in ["immediately", "urgent", "critical", "stop", "quit"]
                ) else "MEDIUM"
                p_class = "critical" if priority == "HIGH" else "warning"
                timeline = "1-2 weeks" if priority == "HIGH" else "4-6 weeks"
                action_items.append((text[:120], priority, p_class, timeline))

    if not action_items:
        action_items = [
            ("Increase vegetables to 5 servings daily", "MEDIUM", "warning", "2-4 weeks"),
            ("Replace refined grains with whole grains", "MEDIUM", "warning", "4-6 weeks"),
            ("Add omega-3 rich foods (fish, flaxseed)", "MEDIUM", "warning", "1-2 weeks"),
            ("Reduce added sugar to under 25g daily", "MEDIUM", "warning", "4-8 weeks"),
        ]

    action_rows = ""
    for text, priority, p_class, timeline in action_items:
        action_rows += f"""
        <tr>
            <td>{text}</td>
            <td><span class="pill {p_class}" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;">{priority}</span></td>
            <td>{timeline}</td>
        </tr>
        """

    # ── Chart.js data ─────────────────────────────────────────────────────────
    trend_datasets = _json.dumps([{
        "label": d["label"],
        "data": [float(d["score"]), float(d["proj_5yr"]), float(d["proj_10yr"]), float(d["proj_20yr"])],
        "borderColor": d["color"],
        "backgroundColor": d["color"],
        "borderWidth": 2,
        "pointRadius": 4,
    } for d in diseases])

    radar_labels = _json.dumps([d["label"] for d in diseases])
    radar_data = _json.dumps([float(d["proj_10yr"]) for d in diseases])

    # ── Build final HTML (matching sample template exactly) ───────────────────
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Health Impact Visualization Report — {patient_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ── Reset & Base ───────────────────────────────────── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg-dark:#0B0E14;
  --bg-card:rgba(22, 27, 34, 0.7);
  --border-color:rgba(255, 255, 255, 0.08);
  --text-main:#E2E8F0;
  --text-muted:#94A3B8;
  --primary:#6366F1; /* Indigo */
  --primary-glow:rgba(99, 102, 241, 0.3);
  --accent:#EC4899; /* Pink */
  --success:#10B981;
  --warning:#F59E0B;
  --danger:#EF4444;
  --info:#3B82F6;
  --radius:20px;
  --shadow:0 10px 30px -5px rgba(0, 0, 0, 0.5);
}}

body{{
  font-family:'Outfit',system-ui,sans-serif;
  color:var(--text-main);
  background-color: var(--bg-dark);
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.15) 0px, transparent 50%);
  min-height:100vh;
  line-height:1.6;
  -webkit-font-smoothing: antialiased;
}}

/* ── Layout ─────────────────────────────────────────── */
.container{{max-width:1200px;margin:0 auto;padding:2rem 1.5rem 4rem}}

/* ── Header ─────────────────────────────────────────── */
.header{{
  text-align:center;
  padding:3rem 0;
  margin-bottom: 2rem;
  position:relative;
}}
.header h1{{
  font-size:3rem;
  font-weight:800;
  letter-spacing:-0.03em;
  line-height: 1.1;
  margin-bottom: 0.5rem;
  background:linear-gradient(135deg, #fff 0%, #94a3b8 100%);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}}
.header .subtitle{{
  color:var(--text-muted);
  font-size:1.1rem;
  font-weight: 400;
}}
.header .meta{{
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  opacity: 0.8;
}}

/* ── Score Ring ─────────────────────────────────────── */
.score-container {{
    display: flex;
    justify-content: center;
    margin-bottom: 3rem;
}}
.score-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 2rem;
    border-radius: var(--radius);
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: var(--shadow);
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}}
.score-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
}}

/* ── Grid System ────────────────────────────────────── */
.grid-2{{display:grid;grid-template-columns:repeat(2, 1fr);gap:1.5rem}}
.grid-3{{display:grid;grid-template-columns:repeat(3, 1fr);gap:1.5rem}}
.grid-span-2{{grid-column: span 2}}

@media(max-width:900px){{.grid-3{{grid-template-columns:1fr}}}}
@media(max-width:700px){{.grid-2{{grid-template-columns:1fr; .grid-span-2{{grid-column: span 1}}}}}}

/* ── Cards ──────────────────────────────────────────── */
.card{{
  background:var(--bg-card);
  border:1px solid var(--border-color);
  border-radius:var(--radius);
  padding:1.8rem;
  backdrop-filter:blur(12px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}}
.card:hover{{
    transform: translateY(-2px);
    box-shadow: var(--shadow);
    border-color: rgba(99, 102, 241, 0.3);
}}
.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.8rem;
}}
.card h2{{
  font-size:1.1rem;
  font-weight:600;
  color:var(--text-main);
  display:flex;
  align-items:center;
  gap:0.6rem;
}}
.card h2 .icon{{font-size:1.2rem}}

/* ── Typography & Elements ──────────────────────────── */
h3.section-title {{
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
    font-weight: 700;
}}

/* Pills */
.pill-list{{display:flex;flex-wrap:wrap;gap:0.5rem;}}
.pill{{
  display:inline-flex;
  align-items: center;
  padding:0.35rem 0.8rem;
  border-radius:6px;
  font-size:0.85rem;
  font-weight:500;
  background:var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
}}
.pill.critical {{ border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.1); color: #FCA5A5; }}
.pill.warning {{ border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.1); color: #FCD34D; }}
.pill.good {{ border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1); color: #6EE7B7; }}
.pill.info {{ border-color: rgba(59, 130, 246, 0.4); background: rgba(59, 130, 246, 0.1); color: #93C5FD; }}

/* ── Detailed Analysis Styles ───────────────────────── */
.detail-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border-color);
}}
.detail-row:last-child {{ border-bottom: none; }}
.metric-value {{
    font-weight: 700;
    font-size: 1.1rem;
}}
.risk-low {{ color: var(--success); }}
.risk-moderate {{ color: var(--warning); }}
.risk-high {{ color: var(--danger); }}

/* ── Recommendations Table ──────────────────────────── */
.rec-table {{ width: 100%; border-collapse: collapse; }}
.rec-table th {{ 
    text-align: left; 
    padding: 0.8rem; 
    color: var(--text-muted); 
    font-size: 0.8rem; 
    border-bottom: 1px solid var(--border-color); /* Added border-bottom for header */
}}
.rec-table td {{ 
    padding: 0.8rem; 
    border-bottom: 1px solid var(--border-color); 
    font-size: 0.9rem; 
}}
.rec-table tr:last-child td {{ border-bottom: none; }}

/* ── Swap Cards ─────────────────────────────────────── */
.swap-container {{
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}}
.swap-item {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
    background: rgba(255,255,255,0.03);
    padding: 0.8rem;
    border-radius: 12px;
}}
.swap-old {{ text-align: right; color: var(--danger); text-decoration: line-through; opacity: 0.7; }}
.swap-arrow {{ color: var(--text-muted); font-size: 0.8rem; }}
.swap-new {{ color: var(--success); font-weight: 600; }}
.swap-reason {{
    grid-column: 1 / -1;
    font-size: 0.8rem;
    color: var(--text-muted);
    text-align: center;
    font-style: italic;
}}

/* ── Footer ─────────────────────────────────────────── */
.footer{{
    text-align:center;
    padding-top: 3rem;
    color: var(--border-color);
    font-size: 0.8rem;
}}

/* ── Charts ─────────────────────────────────────────── */
.chart-container {{
    position: relative;
    height: 250px;
    width: 100%;
}}
.chart-container.tall {{ height: 350px; }}

</style>
</head>
<body>

<div class="container">

  <!-- HEADER -->
  <header class="header">
    <h1>Health Report</h1>
    <div class="subtitle">Comprehensive Risk Analysis & Action Plan</div>
    <div class="meta">
        <span>👤 {patient_name}</span>
        <span>📅 {date_str}</span>
    </div>
  </header>

  <!-- SCORE SECTION -->
  <div class="score-container">
      <div class="score-card">
          <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.1em;">Click Health Score</div>
          <div style="font-size: 4rem; font-weight: 800; line-height: 1; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
              {health_score}
          </div>
          <div style="font-size: 1.2rem; margin-top: 0.5rem; color: {risk_label_color};">{risk_label_text}</div>
      </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="grid-2">
      <div class="card">
        <div class="card-header"><h2><span class="icon">🚨</span> Top Concerns</h2></div>
        <div class="pill-list">{concern_pills}</div>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted);">
            Immediate attention required for these areas to prevent long-term complications.
        </p>
      </div>
      <div class="card">
        <div class="card-header"><h2><span class="icon">✅</span> Recommended Actions</h2></div>
        <div class="pill-list"></div>
        <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted);">
            High-impact lifestyle changes to mitigate identified risks.
        </p>
      </div>
  </div>

  <div style="margin-top: 2rem;"></div>

  <!-- CHARTS ROW -->
  <div class="grid-2">
      <div class="card">
          <div class="card-header"><h2><span class="icon">📈</span> Disease Risk Trends (Projected)</h2></div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
              Estimated risk progression over 5, 10, and 20 years if current lifestyle continues.
          </p>
          <div class="chart-container tall">
              <canvas id="trendChart"></canvas>
          </div>
      </div>
      <div class="card">
          <div class="card-header"><h2><span class="icon">🎯</span> Comparative Risk Radar</h2></div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
              Comparison of your risk profile against optimal health markers.
          </p>
          <div class="chart-container tall">
              <canvas id="radarChart"></canvas>
          </div>
      </div>
  </div>

  <div style="margin-top: 2rem;"></div>

  <!-- DETAILED ANALYSIS -->
  <h3 class="section-title">Detailed Risk Analysis</h3>
  <div class="grid-3">
      {disease_cards_html}
  </div>

  <div style="margin-top: 2rem;"></div>

  <!-- NUTRITION & STATUS -->
  <div class="grid-2">
      <div class="card">
          <div class="card-header"><h2><span class="icon">🥗</span> Nutritional Status</h2></div>
          
          <div style="margin-bottom: 1.5rem;">
              <div class="detail-row">
                  <span>Dietary Quality Score</span>
                  <span class="metric-value risk-high">{diet_score}/100</span>
              </div>
          </div>

          <h3 class="section-title">Deficiencies</h3>
          <div class="pill-list" style="margin-bottom: 1rem;">{deficiency_pills}</div>
          
          <h3 class="section-title">Strengths</h3>
          <div class="pill-list">{strength_pills}</div>
      </div>

      <div class="card">
          <div class="card-header"><h2><span class="icon">🔄</span> Smart Food Swaps</h2></div>
          <div class="swap-container">
              {swaps_html}
          </div>
      </div>
  </div>

  <div style="margin-top: 2rem;"></div>

  <!-- ACTION PLAN -->
  <div class="card">
      <div class="card-header"><h2><span class="icon">🗓️</span> Strategic Action Plan</h2></div>
      <table class="rec-table">
          <thead>
              <tr>
                  <th width="50%">Recommendation</th>
                  <th width="20%">Priority</th>
                  <th width="30%">Timeline</th>
              </tr>
          </thead>
          <tbody>
              {action_rows}
          </tbody>
      </table>
  </div>

  <footer class="footer">
      <p>Health Impact Prediction System &bull; Generated on {date_str}</p>
      <p style="font-size: 0.75rem; margin-top: 0.5rem; opacity: 0.5;">
          DISCLAIMER: This report is for informational purposes only and does not constitute medical advice.
          Consult with a healthcare professional before making significant lifestyle changes.
      </p>
  </footer>

</div>

<!-- CHART LOGIC -->
<script>
    Chart.defaults.font.family = "'Outfit', sans-serif";
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';

    // ── Trend Line Chart ──
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    new Chart(trendCtx, {{
        type: 'line',
        data: {{
            labels: ['Current', '5 Years', '10 Years', '20 Years'],
            datasets: {trend_datasets}
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            tension: 0.4,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ usePointStyle: true, padding: 20 }} }},
                tooltip: {{ 
                    backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                    titleColor: '#fff', 
                    bodyColor: '#cbd5e1', 
                    borderColor: 'rgba(255,255,255,0.1)', 
                    borderWidth: 1,
                    padding: 10
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    max: 100,
                    title: {{ display: true, text: 'Risk Probability (%)' }}
                }}
            }}
        }}
    }});

    // ── Radar Chart ──
    const radarCtx = document.getElementById('radarChart').getContext('2d');
    new Chart(radarCtx, {{
        type: 'radar',
        data: {{
            labels: {radar_labels},
            datasets: [{{
                label: 'Your Risk Profile',
                data: {radar_data},
                backgroundColor: 'rgba(236, 72, 153, 0.2)',
                borderColor: '#EC4899', // Accent Pink
                pointBackgroundColor: '#EC4899',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#EC4899'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                r: {{
                    angleLines: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                    grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                    pointLabels: {{ color: '#E2E8F0', font: {{ size: 11, weight: 500 }} }},
                    ticks: {{ display: false, backdropColor: 'transparent' }},
                    suggestedMin: 0,
                    suggestedMax: 100
                }}
            }},
            plugins: {{ legend: {{ display: false }} }}
        }}
    }});
</script>

</body>
</html>"""
