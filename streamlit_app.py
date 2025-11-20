import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Soup vs Salad vs Sandwich",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS (kept from your starter, slightly trimmed)
st.markdown("""
    <style>
    body { background: linear-gradient(135deg, #f7fbff 0%, #ffffff 100%); }
    .title-container { text-align: center; padding: 2rem 0; border-radius: 15px; margin-bottom: 1rem; animation: fadeIn 0.6s ease-in; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .title-container h1 { color: white; font-size: 2.4em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .question-container { background: white; border-radius: 12px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.06); border-left: 5px solid #667eea; }
    .question-text { font-size: 1.1em; font-weight: 600; color: #222; margin-bottom: 0.8rem; }
    .answer-button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.95em; cursor: pointer; margin: 0.4rem 0; width:100%; }
    .results-container { background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
    .explanation-text { background: #f7fafc; border-left: 4px solid #667eea; padding: 0.8rem; border-radius: 6px; color: #333; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# --------------------
# SESSION STATE INIT
# --------------------
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    # start with equal baseline scores so pie starts at 33.33 each
    st.session_state.scores = {"Soup": 1.0, "Salad": 1.0, "Sandwich": 1.0}
    st.session_state.answers = []  # store chosen option indices / texts
    st.session_state.impact_history = []  # list of (question_idx, option_text, impact_dict)
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False

# --------------------
# QUESTIONS (food attributes)
# each option: text + impact on the *food item* (not the user's personality)
# impacts are additive; we normalize after each choice into percentages for the pie
# --------------------
QUIZ_QUESTIONS = [
    {
        "question": "🌡️ Temperature: How is this food usually served?",
        "options": [
            {"text": "Piping hot (steam, served hot)", "impact": {"Soup": 3.5, "Salad": -1.0, "Sandwich": 0.0}},
            {"text": "Warm (not boiling)", "impact": {"Soup": 2.0, "Salad": 0.0, "Sandwich": 0.5}},
            {"text": "Room temperature", "impact": {"Soup": 0.0, "Salad": 1.0, "Sandwich": 1.0}},
            {"text": "Chilled / cold", "impact": {"Soup": -2.0, "Salad": 2.5, "Sandwich": 1.0}},
        ]
    },
    {
        "question": "🥣 Liquid content: How much liquid/broth does the food contain?",
        "options": [
            {"text": "Mostly liquid (drinkable/sippable)", "impact": {"Soup": 4.0, "Salad": -2.0, "Sandwich": -2.0}},
            {"text": "Chunky liquid (big solids + broth)", "impact": {"Soup": 2.5, "Salad": 0.5, "Sandwich": -1.0}},
            {"text": "Mostly solid with some sauce", "impact": {"Soup": 0.0, "Salad": 1.5, "Sandwich": 1.5}},
            {"text": "Dry/crispy/no liquid", "impact": {"Soup": -3.0, "Salad": 2.5, "Sandwich": 2.0}},
        ]
    },
    {
        "question": "🍞 Bread presence: Is bread the main vehicle or essential?",
        "options": [
            {"text": "Food primarily sits in / on bread (wrap, between slices)", "impact": {"Soup": -2.0, "Salad": -1.0, "Sandwich": 4.0}},
            {"text": "Bread served alongside (toast/roll)", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 1.0}},
            {"text": "No bread present", "impact": {"Soup": 1.0, "Salad": 1.5, "Sandwich": -2.0}},
            {"text": "Sometimes bread, depends on preparation", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 0.5}},
        ]
    },
    {
        "question": "🍴 Typical utensil: How is it usually eaten?",
        "options": [
            {"text": "Spoon (spoon-first)", "impact": {"Soup": 3.5, "Salad": -1.5, "Sandwich": -2.0}},
            {"text": "Fork (fork-first)", "impact": {"Soup": -0.5, "Salad": 2.5, "Sandwich": 0.5}},
            {"text": "By hand (hand-held)", "impact": {"Soup": -3.0, "Salad": -1.0, "Sandwich": 3.5}},
            {"text": "Knife & fork", "impact": {"Soup": 0.0, "Salad": 1.0, "Sandwich": 1.0}},
        ]
    },
    {
        "question": "🥗 Leafy / raw greens: Does the food primarily feature leaves/crisp raw veg?",
        "options": [
            {"text": "Yes — leaves / raw salad base", "impact": {"Soup": -2.0, "Salad": 4.0, "Sandwich": 0.5}},
            {"text": "Some greens but not primary", "impact": {"Soup": 0.0, "Salad": 1.5, "Sandwich": 0.5}},
            {"text": "No leafy greens", "impact": {"Soup": 1.0, "Salad": -1.0, "Sandwich": 1.0}},
            {"text": "Sometimes / varies", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 0.5}},
        ]
    },
    {
        "question": "🚶 Portability: Is the food commonly eaten on-the-go / hand-held?",
        "options": [
            {"text": "Hand-held & portable", "impact": {"Soup": -3.0, "Salad": -1.0, "Sandwich": 4.0}},
            {"text": "Somewhat portable (bowl with lid / wrapped)", "impact": {"Soup": 0.0, "Salad": 0.5, "Sandwich": 1.5}},
            {"text": "Requires plate/table", "impact": {"Soup": 1.5, "Salad": 1.5, "Sandwich": -1.0}},
            {"text": "Depends on serving", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 0.5}},
        ]
    },
    {
        "question": "🥄 Slurpable / sip: Is the food commonly sipped or slurped?",
        "options": [
            {"text": "Yes — sippable / slurpable", "impact": {"Soup": 4.0, "Salad": -2.0, "Sandwich": -2.0}},
            {"text": "Sometimes (brothy parts)", "impact": {"Soup": 2.0, "Salad": 0.0, "Sandwich": -0.5}},
            {"text": "No — not sippable", "impact": {"Soup": -2.0, "Salad": 2.0, "Sandwich": 1.0}},
            {"text": "Not applicable", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 0.5}},
        ]
    },
    {
        "question": "🍽️ Texture: Is the food mostly smooth, chunky, or crisp?",
        "options": [
            {"text": "Smooth/consistent (puree, blended)", "impact": {"Soup": 2.5, "Salad": -1.0, "Sandwich": -0.5}},
            {"text": "Chunky pieces in liquid or sauce", "impact": {"Soup": 1.5, "Salad": 1.0, "Sandwich": 0.5}},
            {"text": "Mostly solid pieces (no significant liquid)", "impact": {"Soup": -2.0, "Salad": 2.0, "Sandwich": 1.5}},
            {"text": "Dry & crispy", "impact": {"Soup": -3.0, "Salad": 3.0, "Sandwich": 2.0}},
        ]
    },
    {
        "question": "⭐ Role in meal: Is this usually a starter, main, side, or snack?",
        "options": [
            {"text": "Starter / appetizer", "impact": {"Soup": 1.0, "Salad": 1.5, "Sandwich": -0.5}},
            {"text": "Main course", "impact": {"Soup": 1.5, "Salad": 1.0, "Sandwich": 1.5}},
            {"text": "Side / small plate", "impact": {"Soup": 0.5, "Salad": 1.0, "Sandwich": 0.5}},
            {"text": "Snack / handheld", "impact": {"Soup": -1.0, "Salad": 0.0, "Sandwich": 2.0}},
        ]
    },
    {
        "question": "🥗 Customizable: Does the food typically get many toppings or mix-ins?",
        "options": [
            {"text": "Lots of toppings & mix-ins", "impact": {"Soup": 0.5, "Salad": 2.5, "Sandwich": 2.0}},
            {"text": "Some customization", "impact": {"Soup": 0.5, "Salad": 1.0, "Sandwich": 1.0}},
            {"text": "Usually fixed / one recipe", "impact": {"Soup": 1.5, "Salad": -0.5, "Sandwich": -0.5}},
            {"text": "Varies", "impact": {"Soup": 0.5, "Salad": 0.5, "Sandwich": 0.5}},
        ]
    }
]

# --------------------
# HELPERS
# --------------------
def normalize_scores(scores_dict):
    """Return normalized percentages (sum to 100). clamp small positives to avoid negative/zero issues."""
    # ensure no negative totals; keep additive baseline
    clamped = {k: max(0.01, float(v)) for k, v in scores_dict.items()}
    total = sum(clamped.values())
    return {k: (v / total * 100) for k, v in clamped.items()}

def plot_pie(percentages):
    """Matplotlib pie to embed in Streamlit — returns fig"""
    labels = [f"{k} ({percentages[k]:.1f}%)" for k in percentages]
    sizes = list(percentages.values())
    colors = ['#FF8A80', '#8CE99A', '#FFD166']  # soup (warm), salad (green), sandwich (warm/yellow)
    fig, ax = plt.subplots(figsize=(4,4), dpi=100)
    wedges, texts = ax.pie(sizes, labels=labels, startangle=140, colors=colors, wedgeprops=dict(width=0.5))
    ax.set(aspect="equal")
    return fig

# --------------------
# RENDER TITLE
# --------------------
st.markdown("""
    <div class="title-container">
        <h1>🍲 SOUP vs SALAD vs SANDWICH</h1>
        <p style="color: #f0f2f8; margin-top: 0.2rem;">Evaluate one *food item* — answer attribute questions about the food, not your personality.</p>
    </div>
""", unsafe_allow_html=True)

# --------------------
# LAYOUT: left = quiz, right = live pie + history
# --------------------
left, right = st.columns([2, 1])

with right:
    st.markdown("<div class='results-container'>", unsafe_allow_html=True)
    st.markdown("### Live classification")
    # compute and show current pie chart (normalize baseline then after impacts)
    percentages = normalize_scores(st.session_state.scores)
    st.pyplot(plot_pie(percentages))
    st.markdown("**Current percentages**")
    st.write(pd.DataFrame({
        "Label": list(percentages.keys()),
        "Percent": [f"{v:.1f}%" for v in percentages.values()],
        "Raw score": [f"{st.session_state.scores[k]:.2f}" for k in percentages.keys()]
    }).set_index("Label"))
    st.markdown("---")
    st.markdown("### Impact history (recent)")
    if len(st.session_state.impact_history) == 0:
        st.write("No attributes answered yet. The pie starts at 33.33% each.")
    else:
        # show last 6 impacts
        for qidx, opt_text, impact in st.session_state.impact_history[-6:][::-1]:
            st.markdown(f"**Q{qidx+1}** • {opt_text}")
            # show small summary of how that answer moved the raw scores
            deltas = ", ".join([f"{k}: {impact[k]:+g}" for k in ["Soup","Salad","Sandwich"]])
            st.markdown(f"*Impact —* {deltas}")
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# QUIZ FLOW on left
# --------------------
with left:
    if not st.session_state.quiz_started and not st.session_state.quiz_completed:
        st.markdown("""
            <div class="question-container">
                <h3 class="question-text">Ready to analyze a food item?</h3>
                <p>Answer questions about the **food** (how it is served / its texture / presence of bread / etc.). After each answer the pie updates.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start analysis", use_container_width=True):
            st.session_state.quiz_started = True
            st.experimental_rerun()

    elif st.session_state.quiz_completed:
        # final screen with explanation and reset
        st.markdown("<div class='question-container'>", unsafe_allow_html=True)
        st.markdown("## ✅ Analysis complete")
        pct = normalize_scores(st.session_state.scores)
        winner = max(pct, key=pct.get)
        st.markdown(f"### Result: **{winner}** — {pct[winner]:.1f}%")
        st.markdown("#### Why (top contributing attributes)")
        # compute simple contribution totals per label from impact_history
        contrib = {"Soup": 0.0, "Salad": 0.0, "Sandwich": 0.0}
        for _, _, imp in st.session_state.impact_history:
            for k in contrib:
                contrib[k] += imp.get(k, 0.0)
        # show top 3 attributes that increased each label
        st.write(pd.DataFrame([
            {"Label": k, "Total impact": f"{contrib[k]:+.2f}", "Final raw score": f"{st.session_state.scores[k]:.2f}"}
            for k in contrib
        ]).set_index("Label"))
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔄 Analyze another food (reset)", use_container_width=True):
            st.session_state.current_question = 0
            st.session_state.scores = {"Soup": 1.0, "Salad": 1.0, "Sandwich": 1.0}
            st.session_state.answers = []
            st.session_state.impact_history = []
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.experimental_rerun()

    else:
        # render current question (about the food)
        qidx = st.session_state.current_question
        qdata = QUIZ_QUESTIONS[qidx]

        progress_col1, progress_col2 = st.columns([1, 4])
        with progress_col1:
            st.metric("Question", f"{qidx+1}/{len(QUIZ_QUESTIONS)}")
        with progress_col2:
            st.progress(qidx / len(QUIZ_QUESTIONS))

        st.markdown(f"<div class='question-container'><div class='question-text'>{qdata['question']}</div></div>", unsafe_allow_html=True)

        # present options as buttons (2 columns)
        opt_cols = st.columns(2)
        for i, opt in enumerate(qdata["options"]):
            with opt_cols[i % 2]:
                btn_key = f"q{qidx}_opt{i}"
                # use st.button for choice; when clicked, apply impact and advance
                if st.button(opt["text"], key=btn_key):
                    # apply impact (additive)
                    for label, delta in opt["impact"].items():
                        st.session_state.scores[label] = st.session_state.scores.get(label, 0.0) + delta
                    # record answer & impact for explainability
                    st.session_state.answers.append((qidx, opt["text"]))
                    st.session_state.impact_history.append((qidx, opt["text"], opt["impact"]))
                    # advance
                    st.session_state.current_question += 1
                    if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                        st.session_state.quiz_completed = True
                    # rerun to update pie live
                    st.experimental_rerun()

        # small "skip / unsure" option: apply neutral small impacts and advance
        if st.button("Skip / Not sure (apply neutral)", key=f"q{qidx}_skip"):
            neutral = {"Soup": 0.2, "Salad": 0.2, "Sandwich": 0.2}
            for label, delta in neutral.items():
                st.session_state.scores[label] = st.session_state.scores.get(label, 0.0) + delta
            st.session_state.answers.append((qidx, "Skipped / unsure"))
            st.session_state.impact_history.append((qidx, "Skipped / unsure", neutral))
            st.session_state.current_question += 1
            if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                st.session_state.quiz_completed = True
            st.experimental_rerun()