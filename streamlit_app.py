# app.py
import streamlit as st
import json
from math import isclose

st.set_page_config(page_title="Soup / Salad / Sandwich Classifier", layout="wide",
                   initial_sidebar_state="expanded")

# -------------------------
# Core classifier (adapted from demo)
# -------------------------
feature_weights_default = {
    'temperature': 0.10,
    'utensil': 0.15,
    'container': 0.15,
    'submersion': 0.30,
    'dressing_coating': 0.20,
    'discrete_pieces': 0.25,
    'bread_presence': 0.30,
    'portability': 0.15,
}

temperature_map = {
    'hot': {'soup':1.0, 'salad':0.0, 'sandwich':0.0},
    'warm':{'soup':0.8, 'salad':0.1, 'sandwich':0.1},
    'room':{'soup':0.2, 'salad':0.8, 'sandwich':0.5},
    'cold':{'soup':0.0, 'salad':1.0, 'sandwich':0.5},
}

utensil_map = {
    'spoon': {'soup':1.0, 'salad':0.1, 'sandwich':0.0},
    'fork': {'soup':0.2, 'salad':0.9, 'sandwich':0.1},
    'knife & fork': {'soup':0.1, 'salad':0.7, 'sandwich':0.4},
    'hand': {'soup':0.0, 'salad':0.3, 'sandwich':1.0},
}

container_map = {
    'bowl': {'soup':1.0, 'salad':0.2, 'sandwich':0.0},
    'plate': {'soup':0.1, 'salad':0.8, 'sandwich':0.2},
    'bread / bun': {'soup':0.0, 'salad':0.2, 'sandwich':1.0},
    'bread bowl': {'soup':0.9, 'salad':0.1, 'sandwich':0.2},
    'none / wrapper': {'soup':0.1, 'salad':0.4, 'sandwich':0.4},
}

def classify(features, weights):
    # read features with defaults
    temp = features.get('temperature','room')
    utensil = features.get('utensil','fork')
    container = features.get('container','plate')
    submersion = float(features.get('submersion', 0.0))
    dressing = float(features.get('dressing_coating', 0.0))
    discrete = 1.0 if features.get('discrete_pieces', False) else 0.0
    bread = 1.0 if features.get('bread_presence', False) else 0.0
    portability = float(features.get('portability', 0.0))
    raw = {'soup':0.0, 'salad':0.0, 'sandwich':0.0}

    # temp
    tmap = temperature_map.get(temp, temperature_map['room'])
    raw['soup'] += weights['temperature'] * tmap['soup']
    raw['salad'] += weights['temperature'] * tmap['salad']
    raw['sandwich'] += weights['temperature'] * tmap['sandwich']

    # utensil
    umap = utensil_map.get(utensil, utensil_map['fork'])
    raw['soup'] += weights['utensil'] * umap['soup']
    raw['salad'] += weights['utensil'] * umap['salad']
    raw['sandwich'] += weights['utensil'] * umap['sandwich']

    # container
    cmap = container_map.get(container, container_map['plate'])
    raw['soup'] += weights['container'] * cmap['soup']
    raw['salad'] += weights['container'] * cmap['salad']
    raw['sandwich'] += weights['container'] * cmap['sandwich']

    # numeric features
    raw['soup'] += weights['submersion'] * submersion
    raw['salad'] += weights['submersion'] * (1.0 - submersion) * 0.3
    raw['sandwich'] += weights['submersion'] * (1.0 - submersion) * 0.1

    raw['salad'] += weights['dressing_coating'] * dressing
    raw['soup'] += weights['dressing_coating'] * dressing * 0.05
    raw['sandwich'] += weights['dressing_coating'] * dressing * 0.05

    raw['salad'] += weights['discrete_pieces'] * discrete
    raw['soup'] += weights['discrete_pieces'] * (1.0 - discrete) * 0.05

    raw['sandwich'] += weights['bread_presence'] * bread
    raw['soup'] += weights['bread_presence'] * bread * 0.02
    raw['salad'] += weights['bread_presence'] * bread * 0.05

    raw['sandwich'] += weights['portability'] * portability
    raw['salad'] += weights['portability'] * (1.0 - portability) * 0.2
    raw['soup'] += weights['portability'] * (1.0 - portability) * 0.1

    total = raw['soup'] + raw['salad'] + raw['sandwich']
    if isclose(total, 0.0):
        pct = {'soup':33.3, 'salad':33.3, 'sandwich':33.3}
    else:
        pct = {k: round((v/total)*100,1) for k,v in raw.items()}

    sorted_pct = sorted(pct.items(), key=lambda kv: kv[1], reverse=True)
    top_label, top_val = sorted_pct[0]
    explanation_lines = []
    explanation_lines.append(f"Raw scores: {raw}")
    explanation_lines.append(f"Normalized percentages: {pct}")
    explanation_lines.append(f"Top: {top_label} ({top_val}%)")
    if abs(top_val - sorted_pct[1][1]) < 8.0:
        explanation_lines.append("⚠️ Close call — this is a borderline/ambiguous classification.")
    # human-readable reasons
    explanation_lines.append(f"Temperature -> {temp}; Utensil -> {utensil}; Container -> {container}.")
    explanation_lines.append(f"Submersion={submersion}; Dressing={dressing}; DiscretePieces={bool(discrete)}; Bread={bool(bread)}; Portability={portability}.")
    return {'percentages': pct, 'majority': top_label, 'majority_percent': top_val,
            'raw': raw, 'explanation': "\n".join(explanation_lines)}

# -------------------------
# Styling + header
# -------------------------
PAGE_CSS = """
<style>
/* page background gradient */
.stApp {
  background: linear-gradient(180deg, #0f172a 0%, #07103a 45%, #07103a 100%);
  color: #e6eef8;
  font-family: Inter, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}

/* card look */
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.6);
  transition: transform 0.28s ease, box-shadow 0.28s ease;
}
.card:hover { transform: translateY(-6px); box-shadow: 0 12px 28px rgba(2,6,23,0.7); }

/* small headers */
.small-muted { color: #9fb2d3; font-size:0.9rem; }

/* animated counters (for accessibility fallback) */
.counter { font-weight:700; font-size:1.6rem; }

/* layout tweaks */
.row-gap { margin-bottom: 12px; }

/* tiny ticker */
.tiny { font-size:0.85rem; color:#bcd0f0; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1], gap="large")
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0'>Soup • Salad • Sandwich</h1>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>A tunable classifier. Slide weights, change inputs, watch the percentages.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex; gap:12px; align-items:center;'>"
                "<div style='font-weight:700;'>Theme</div>"
                "<div style='color:#9fb2d3;'>Modern · Playful</div>"
                "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Sidebar inputs
# -------------------------
st.sidebar.markdown("## Inputs & Presets")

preset = st.sidebar.selectbox("Quick presets", ["Custom", "Tomato Soup", "Caesar Salad", "BLT Sandwich", "Gazpacho", "Bread-bowl Chili", "Soft Taco"])
food_name = st.sidebar.text_input("Food name", value="Custom Food" if preset == "Custom" else preset)

# main features
st.sidebar.markdown("### Features")
temperature = st.sidebar.selectbox("Temperature", options=list(temperature_map.keys()), index=2)
utensil = st.sidebar.selectbox("Utensil", options=list(utensil_map.keys()), index=1)
container = st.sidebar.selectbox("Container", options=list(container_map.keys()), index=1)
submersion = st.sidebar.slider("Submersion (0 = none, 1 = fully submerged)", 0.0, 1.0, 0.0, 0.05)
dressing = st.sidebar.slider("Dressing / coating (0-1)", 0.0, 1.0, 0.0, 0.05)
discrete = st.sidebar.checkbox("Discrete pieces (salad-like)", value=False)
bread_presence = st.sidebar.checkbox("Bread / starchy boundary present", value=False)
portability = st.sidebar.slider("Portability / hand-eaten (0-1)", 0.0, 1.0, 0.0, 0.05)

# show preset override
if preset != "Custom":
    if preset == "Tomato Soup":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "hot", "spoon", "bowl", 1.0, 0.0, False, False, 0.0
    elif preset == "Caesar Salad":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "room", "fork", "plate", 0.0, 0.6, True, False, 0.2
    elif preset == "BLT Sandwich":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "room", "hand", "bread / bun", 0.0, 0.1, False, True, 1.0
    elif preset == "Gazpacho":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "cold", "spoon", "bowl", 0.9, 0.0, False, False, 0.0
    elif preset == "Soft Taco":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "warm", "hand", "bread / bun", 0.0, 0.2, True, True, 0.9
    elif preset == "Bread-bowl Chili":
        temperature, utensil, container, submersion, dressing, discrete, bread_presence, portability = \
            "hot", "spoon", "bread bowl", 0.8, 0.0, False, True, 0.3

st.sidebar.markdown("---")
st.sidebar.markdown("### Weights (drag to tune importance)")
w_temp = st.sidebar.slider("Temperature weight", 0.0, 0.5, float(feature_weights_default['temperature']), 0.01)
w_utensil = st.sidebar.slider("Utensil weight", 0.0, 0.5, float(feature_weights_default['utensil']), 0.01)
w_container = st.sidebar.slider("Container weight", 0.0, 0.5, float(feature_weights_default['container']), 0.01)
w_sub = st.sidebar.slider("Submersion weight", 0.0, 1.0, float(feature_weights_default['submersion']), 0.01)
w_dress = st.sidebar.slider("Dressing weight", 0.0, 1.0, float(feature_weights_default['dressing_coating']), 0.01)
w_discrete = st.sidebar.slider("Discrete pieces weight", 0.0, 1.0, float(feature_weights_default['discrete_pieces']), 0.01)
w_bread = st.sidebar.slider("Bread presence weight", 0.0, 1.0, float(feature_weights_default['bread_presence']), 0.01)
w_port = st.sidebar.slider("Portability weight", 0.0, 1.0, float(feature_weights_default['portability']), 0.01)

weights = {
    'temperature': w_temp, 'utensil': w_utensil, 'container': w_container,
    'submersion': w_sub, 'dressing_coating': w_dress, 'discrete_pieces': w_discrete,
    'bread_presence': w_bread, 'portability': w_port
}

# -------------------------
# Run classifier
# -------------------------
features = {
    'temperature': temperature,
    'utensil': utensil,
    'container': container,
    'submersion': submersion,
    'dressing_coating': dressing,
    'discrete_pieces': discrete,
    'bread_presence': bread_presence,
    'portability': portability
}

result = classify(features, weights)

# -------------------------
# Results area (main)
# -------------------------
left, right = st.columns([1, 1], gap="large")
with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='margin:4px 0'>{food_name}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='tiny'>Majority: <strong>{result['majority']}</strong> — {result['majority_percent']}%</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    # Embed animated circular progress using HTML/JS
    # We pass the percentages into the html snippet so it animates to the final value
    pct_json = json.dumps(result['percentages'])
    circular_widget = f"""
    <div id="radial-container" style="display:flex;gap:18px;justify-content:flex-start;align-items:center;">
      <div style="width:140px;">
        <div id="c-soup" style="width:140px;height:140px;border-radius:70px;display:flex;align-items:center;justify-content:center;background:conic-gradient(#2dd4bf 0 0%, rgba(255,255,255,0.08) 0% 100%);transition: all 1s ease;"></div>
        <div style="text-align:center;margin-top:8px;font-weight:700;">Soup</div>
      </div>
      <div style="width:140px;">
        <div id="c-salad" style="width:140px;height:140px;border-radius:70px;display:flex;align-items:center;justify-content:center;background:conic-gradient(#60a5fa 0 0%, rgba(255,255,255,0.08) 0% 100%);transition: all 1s ease;"></div>
        <div style="text-align:center;margin-top:8px;font-weight:700;">Salad</div>
      </div>
      <div style="width:140px;">
        <div id="c-sandwich" style="width:140px;height:140px;border-radius:70px;display:flex;align-items:center;justify-content:center;background:conic-gradient(#f97316 0 0%, rgba(255,255,255,0.08) 0% 100%);transition: all 1s ease;"></div>
        <div style="text-align:center;margin-top:8px;font-weight:700;">Sandwich</div>
      </div>
    </div>

    <script>
    const pct = {pct_json};
    // animate conic-gradient to percentage
    function animateCircle(id, val, color) {{
      const el = document.getElementById(id);
      if(!el) return;
      // inner text element
      el.innerHTML = '<div style="font-weight:800;color:white;font-size:20px;">0%</div>';
      setTimeout(()=> {{
        const circleVal = Math.round(val);
        el.style.background = `conic-gradient(${color} 0% ${circleVal}%, rgba(255,255,255,0.06) ${circleVal}% 100%)`;
        el.innerHTML = '<div style="font-weight:800;color:white;font-size:20px;">'+circleVal+'%</div>';
      }}, 120);
    }}
    animateCircle('c-soup', pct.soup, '#06b6d4');
    animateCircle('c-salad', pct.salad, '#3b82f6');
    animateCircle('c-sandwich', pct.sandwich, '#fb923c');
    </script>
    """
    st.components.v1.html(circular_widget, height=220)

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Quick temperature / utensil / container summary</div>", unsafe_allow_html=True)
    st.write(f"Temperature: **{temperature}** · Utensil: **{utensil}** · Container: **{container}**")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0'>Model reasoning</h3>", unsafe_allow_html=True)
    st.markdown("<div class='tiny' style='margin-bottom:8px'>Why the model picked what it did</div>", unsafe_allow_html=True)
    st.write(result['explanation'])
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Raw scores (debug)</div>", unsafe_allow_html=True)
    st.json(result['raw'])
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Tweak & experiment panel
# -------------------------
st.markdown("<div class='card' style='margin-top:18px;'>", unsafe_allow_html=True)
left2, mid2, right2 = st.columns([1,1,1])
with left2:
    st.markdown("### Try ambiguous foods")
    if st.button("Toggle: Make it ambiguous (sandwich↔salad)"):
        # mutate features to ambiguous
        features['dressing_coating'] = 0.6
        features['bread_presence'] = True
        features['portability'] = 0.6
        result = classify(features, weights)
        st.experimental_rerun()
    st.write("Or use presets in the sidebar.")

with mid2:
    st.markdown("### Save config")
    if st.button("Copy config to clipboard (JSON)"):
        config = {'food_name': food_name, 'features': features, 'weights': weights}
        st.write("Config JSON (copy from below):")
        st.code(json.dumps(config, indent=2))

with right2:
    st.markdown("### Export")
    if st.button("Export result as text"):
        out_txt = f"{food_name} -> {result['majority']} ({result['majority_percent']}%)\\n\\nDetails:\\n{result['explanation']}"
        st.download_button("Download result .txt", out_txt, file_name=f"{food_name}_classification.txt", mime="text/plain")

st.markdown("</div>", unsafe_allow_html=True)

# footer
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<div class='tiny' style='text-align:center'>Built for vibes — tune weights to fit your take. — enjoy.</div>", unsafe_allow_html=True)
