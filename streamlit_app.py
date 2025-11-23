import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Food Classifier",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - dark theme and contrast-safe colors
st.markdown("""
    <style>
    body { background: linear-gradient(135deg, #0b1226 0%, #17233d 100%); color: #e6eef8; }
    .title-container { 
        text-align: center; 
        padding: 1.6rem 0; 
        border-radius: 12px; 
        margin-bottom: 1rem; 
        animation: fadeIn 0.6s ease-in; 
        background: linear-gradient(135deg, #15284b 0%, #223a66 100%); 
    }
    .title-container h1 { 
        color: #f8fbff; 
        font-size: 2.2em; 
        margin: 0; 
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6); 
    }
    .title-container p { color: #dceeff; margin-top: 0.25rem }

    /* Dark cards for questions and results */
    .question-container { 
        background: linear-gradient(180deg, #0f2138 0%, #0b1a2d 100%); 
        border-radius: 10px; 
        padding: 1.2rem; 
        margin: 0.8rem 0; 
        box-shadow: 0 6px 20px rgba(5,12,30,0.6); 
        border-left: 4px solid #274b94; 
    }
    .question-text { 
        font-size: 1.05em; 
        font-weight: 700; 
        color: #eaf3ff; 
        margin-bottom: 0.9rem; 
    }
    .results-container { 
        background: linear-gradient(180deg, #0f2138 0%, #071425 100%); 
        border-radius: 10px; 
        padding: 1rem; 
        box-shadow: 0 6px 24px rgba(3,8,20,0.65); 
        color: #eaf3ff;
    }
    .explanation-box { background: transparent; padding: 0.6rem; border-left: 3px solid #274b94; color: #dceeff; margin: 0.4rem 0; }
    .reasoning-box { background: rgba(255,255,255,0.02); padding: 0.8rem; border-radius: 6px; color: #e6f0ff; margin: 0.4rem 0; }

    /* Buttons and radio styling fallback */
    .stButton>button { background: linear-gradient(90deg,#2b4f9b,#3b6fb2); color: white; }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.soup_pct = 33.33
    st.session_state.salad_pct = 33.33
    st.session_state.sandwich_pct = 33.33
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False
    st.session_state.answers = {}
    st.session_state.reasoning_data = []

# Food classification questions (10 questions - streamlined)
QUIZ_QUESTIONS = [
    {
        "question": "How is this food usually served?",
        "options": [
            {"text": "Piping hot with steam", "soup": 20, "salad": -10, "sandwich": 0, "reason_soup": "Hot temperature is classic for soups", "reason_salad": "Salads are typically cold", "reason_sandwich": "Temperature varies for sandwiches"},
            {"text": "Warm", "soup": 10, "salad": 0, "sandwich": 5, "reason_soup": "Warm works for some soups", "reason_salad": "Neutral for salad", "reason_sandwich": "Warm sandwiches exist"},
            {"text": "Room temperature", "soup": 0, "salad": 5, "sandwich": 5, "reason_soup": "Room temp is unusual for soup", "reason_salad": "Common for salads", "reason_sandwich": "Common for sandwiches"},
            {"text": "Cold or chilled", "soup": -15, "salad": 25, "sandwich": 5, "reason_soup": "Cold ruins most soups", "reason_salad": "Salads are typically cold", "reason_sandwich": "Cold sandwiches are common"},
        ]
    },
    {
        "question": "How much liquid or broth does it contain?",
        "options": [
            {"text": "Mostly liquid or broth", "soup": 25, "salad": -15, "sandwich": -20, "reason_soup": "High liquid content defines soup", "reason_salad": "Salads are not liquid-based", "reason_sandwich": "Bread-based foods aren't liquid"},
            {"text": "Some liquid with solid chunks", "soup": 15, "salad": 0, "sandwich": -5, "reason_soup": "Chunky soups are classic", "reason_salad": "Minimal liquid for salad", "reason_sandwich": "Not typical for sandwiches"},
            {"text": "Mostly dry with light sauce", "soup": -10, "salad": 15, "sandwich": 10, "reason_soup": "Dry contradicts soup nature", "reason_salad": "Salads are generally dry", "reason_sandwich": "Dry works for sandwiches"},
            {"text": "Completely dry, no liquid", "soup": -25, "salad": 20, "sandwich": 20, "reason_soup": "No liquid means not soup", "reason_salad": "Dry fits salad profile", "reason_sandwich": "Dry fits sandwich profile"},
        ]
    },
    {
        "question": "Is bread the main vessel or essential component?",
        "options": [
            {"text": "Yes, food is in or on bread", "soup": -20, "salad": -10, "sandwich": 30, "reason_soup": "Bread is not core to soup", "reason_salad": "Salad doesn't center on bread", "reason_sandwich": "Bread is the defining feature"},
            {"text": "Bread served on the side", "soup": 5, "salad": 5, "sandwich": 10, "reason_soup": "Bread as side is optional", "reason_salad": "Bread complements but not required", "reason_sandwich": "Bread enhances sandwiches"},
            {"text": "No bread involved", "soup": 10, "salad": 15, "sandwich": -15, "reason_soup": "No bread is typical for soup", "reason_salad": "No bread is typical for salad", "reason_sandwich": "Bread-free means not sandwich"},
            {"text": "Sometimes, varies", "soup": 0, "salad": 5, "sandwich": 0, "reason_soup": "Variable bread doesn't help", "reason_salad": "Can be flexible", "reason_sandwich": "Inconsistent with sandwich"},
        ]
    },
    {
        "question": "How is it typically eaten?",
        "options": [
            {"text": "With a spoon", "soup": 25, "salad": -10, "sandwich": -20, "reason_soup": "Spoon is the soup tool", "reason_salad": "Forks are better for salad", "reason_sandwich": "Hand or utensils, not spoon"},
            {"text": "With a fork", "soup": -10, "salad": 25, "sandwich": 0, "reason_soup": "Fork is unsuitable for soup", "reason_salad": "Fork is the salad standard", "reason_sandwich": "Neutral for sandwiches"},
            {"text": "With hands", "soup": -20, "salad": 0, "sandwich": 25, "reason_soup": "Hard to eat soup by hand", "reason_salad": "Possible but not typical", "reason_sandwich": "Hand-held is sandwich signature"},
            {"text": "Knife and fork", "soup": 0, "salad": 10, "sandwich": 10, "reason_soup": "Knife fork for soup is uncommon", "reason_salad": "Works for substantial salads", "reason_sandwich": "Works for some sandwiches"},
        ]
    },
    {
        "question": "Does it feature fresh leafy greens or raw vegetables as a main component?",
        "options": [
            {"text": "Yes, leaves or raw veggies are primary", "soup": -20, "salad": 30, "sandwich": 5, "reason_soup": "Fresh greens aren't soup base", "reason_salad": "Fresh greens define salad", "reason_sandwich": "Greens add to sandwiches"},
            {"text": "Some greens but not main", "soup": 0, "salad": 10, "sandwich": 5, "reason_soup": "Few greens okay for soup", "reason_salad": "Supportive role for greens", "reason_sandwich": "Greens support sandwich"},
            {"text": "No leafy greens", "soup": 10, "salad": -15, "sandwich": 10, "reason_soup": "Many soups have no greens", "reason_salad": "No greens hurts salad identity", "reason_sandwich": "Greens optional in sandwiches"},
            {"text": "Varies by preparation", "soup": 0, "salad": 0, "sandwich": 0, "reason_soup": "Variable doesn't help classify", "reason_salad": "Variable doesn't help classify", "reason_sandwich": "Variable doesn't help classify"},
        ]
    },
    {
        "question": "Is it portable and commonly eaten on the go?",
        "options": [
            {"text": "Very portable, hand-held", "soup": -25, "salad": -5, "sandwich": 30, "reason_soup": "Soups spill when mobile", "reason_salad": "Salads need containment", "reason_sandwich": "Sandwiches are grab and go"},
            {"text": "Somewhat portable", "soup": 0, "salad": 5, "sandwich": 10, "reason_soup": "Soups need careful transport", "reason_salad": "Salads can travel in containers", "reason_sandwich": "Most sandwiches are portable"},
            {"text": "Not very portable", "soup": 10, "salad": 5, "sandwich": -10, "reason_soup": "Soups are eaten at table", "reason_salad": "Salads eaten at table", "reason_sandwich": "Sandwiches are usually portable"},
            {"text": "Depends on serving style", "soup": 0, "salad": 0, "sandwich": 0, "reason_soup": "Variable doesn't indicate", "reason_salad": "Variable doesn't indicate", "reason_sandwich": "Variable doesn't indicate"},
        ]
    },
    {
        "question": "Can it be sipped or slurped?",
        "options": [
            {"text": "Yes, it is sippable or slurpable", "soup": 30, "salad": -20, "sandwich": -20, "reason_soup": "Sipping is soup characteristic", "reason_salad": "Salads cannot be sipped", "reason_sandwich": "Sandwiches cannot be sipped"},
            {"text": "Partially, some parts are sippable", "soup": 15, "salad": 0, "sandwich": 0, "reason_soup": "Some liquid to sip indicates soup", "reason_salad": "Not typical for salad", "reason_sandwich": "Not typical for sandwich"},
            {"text": "No, not sippable", "soup": -20, "salad": 15, "sandwich": 15, "reason_soup": "Non-sippable isn't soup", "reason_salad": "Salads aren't sippable", "reason_sandwich": "Sandwiches aren't sippable"},
            {"text": "Not applicable", "soup": 0, "salad": 0, "sandwich": 0, "reason_soup": "Can't determine", "reason_salad": "Can't determine", "reason_sandwich": "Can't determine"},
        ]
    },
    {
        "question": "What is the primary role of this food in a meal?",
        "options": [
            {"text": "Starter or appetizer", "soup": 15, "salad": 10, "sandwich": -5, "reason_soup": "Soups are classic starters", "reason_salad": "Salads work as openers", "reason_sandwich": "Sandwiches are usually mains"},
            {"text": "Main course", "soup": 5, "salad": 0, "sandwich": 15, "reason_soup": "Soups can be mains", "reason_salad": "Salads rarely main focus", "reason_sandwich": "Sandwiches are main courses"},
            {"text": "Side or small plate", "soup": 0, "salad": 15, "sandwich": 0, "reason_soup": "Soups standalone", "reason_salad": "Salads work as sides", "reason_sandwich": "Sandwiches are substantial"},
            {"text": "Snack", "soup": -10, "salad": 0, "sandwich": 20, "reason_soup": "Soups aren't typical snacks", "reason_salad": "Salads not common snacks", "reason_sandwich": "Sandwiches are perfect snacks"},
        ]
    },
    {
        "question": "Does it have multiple toppings or customizable components?",
        "options": [
            {"text": "Lots of toppings or variations", "soup": 0, "salad": 20, "sandwich": 20, "reason_soup": "Soups are fixed recipes", "reason_salad": "Salads thrive on toppings", "reason_sandwich": "Sandwiches are very customizable"},
            {"text": "Some customization options", "soup": 5, "salad": 10, "sandwich": 10, "reason_soup": "Some soups allow tweaks", "reason_salad": "Moderate customization typical", "reason_sandwich": "Common to customize"},
            {"text": "Fixed recipe, no variations", "soup": 15, "salad": -10, "sandwich": -5, "reason_soup": "Fixed recipes common for soups", "reason_salad": "Salads invite customization", "reason_sandwich": "Sandwiches are customizable"},
            {"text": "Varies", "soup": 0, "salad": 0, "sandwich": 0, "reason_soup": "Can't determine", "reason_salad": "Can't determine", "reason_sandwich": "Can't determine"},
        ]
    },
    {
        "question": "What texture or consistency best describes it?",
        "options": [
            {"text": "Smooth and creamy", "soup": 20, "salad": -10, "sandwich": 0, "reason_soup": "Creamy soups are common", "reason_salad": "Salads are crisp not creamy", "reason_sandwich": "Not typical for sandwiches"},
            {"text": "Chunky pieces in broth", "soup": 20, "salad": 5, "sandwich": -5, "reason_soup": "Classic chunky soup", "reason_salad": "Some texture variety", "reason_sandwich": "Less common structure"},
            {"text": "Crisp and crunchy", "soup": -20, "salad": 25, "sandwich": 15, "reason_soup": "Crispy contradicts soup", "reason_salad": "Crisp texture is salad signature", "reason_sandwich": "Crispy crusts common"},
            {"text": "Mixed textures", "soup": 5, "salad": 15, "sandwich": 20, "reason_soup": "Some texture variety okay", "reason_salad": "Multiple textures in salad", "reason_sandwich": "Layers have varied texture"},
        ]
    },
]

# Helper function to normalize percentages
def normalize_pcts(soup, salad, sandwich):
    """Normalize to 100 total and ensure no negatives"""
    soup = max(0.01, soup)
    salad = max(0.01, salad)
    sandwich = max(0.01, sandwich)
    total = soup + salad + sandwich
    return (soup / total * 100, salad / total * 100, sandwich / total * 100)

def create_pie_chart(soup_pct, salad_pct, sandwich_pct):
    fig = go.Figure(data=[go.Pie(
    labels=['SOUP', 'SALAD', 'SANDWICH'],
    values=[soup_pct, salad_pct, sandwich_pct],
    marker=dict(colors=['#FF5252', '#00C853', '#FFD32F']),  # more vibrant
    textposition='inside',
    texttemplate='%{label}<br>%{value:.1f}%',
    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
    textfont=dict(size=14, color='#222222'),  # dark text for readability
    marker_line=dict(color='white', width=2)
)])

    fig.update_layout(
        showlegend=False,
        height=400,
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig


# Get the winner and build reasoning
def get_winner_analysis(soup_pct, salad_pct, sandwich_pct, reasoning_data):
    percentages = {"SOUP": soup_pct, "SALAD": salad_pct, "SANDWICH": sandwich_pct}
    winner = max(percentages, key=percentages.get)
    
    # Extract key reasons that contributed to this classification
    soup_reasons = []
    salad_reasons = []
    sandwich_reasons = []
    
    for q_idx, option_text, impacts, opt_obj in reasoning_data:
        reason_key_soup = f"reason_soup"
        reason_key_salad = f"reason_salad"
        reason_key_sandwich = f"reason_sandwich"
        
        # Find the option that was selected (if we didn't already store it)
        selected_option = None
        if isinstance(opt_obj, dict) and opt_obj:
            selected_option = opt_obj
        else:
            for opt in QUIZ_QUESTIONS[q_idx]["options"]:
                if opt["text"] == option_text:
                    selected_option = opt
                    break
        
        if selected_option:
            if reason_key_soup in selected_option:
                soup_reasons.append(selected_option[reason_key_soup])
            if reason_key_salad in selected_option:
                salad_reasons.append(selected_option[reason_key_salad])
            if reason_key_sandwich in selected_option:
                sandwich_reasons.append(selected_option[reason_key_sandwich])
    
    return winner, soup_reasons, salad_reasons, sandwich_reasons


def build_two_reason_summary(winner, reasoning_data):
    """Build exactly two concise reasons: either two supporting reasons for the winner,
    or one opposing + one supporting. Returns a single string (one or two sentences).
    """
    def clean(text):
        if not text:
            return ""
        return text.replace('—', ',').replace('*', '').strip()

    key = winner.lower()
    supporting = []  # (magnitude, text)
    opposing = []

    for q_idx, option_text, impacts, opt_obj in reasoning_data:
        if not impacts or key not in impacts:
            continue
        val = impacts.get(key, 0)
        # Find explicit reason string from option object if available
        reason_text = None
        if isinstance(opt_obj, dict):
            reason_text = opt_obj.get(f"reason_{key}")
        if not reason_text:
            reason_text = option_text

        reason_text = clean(reason_text)
        if val > 0:
            supporting.append((val, reason_text))
        elif val < 0:
            opposing.append((abs(val), reason_text))

    # sort by magnitude desc
    supporting.sort(reverse=True, key=lambda x: x[0])
    opposing.sort(reverse=True, key=lambda x: x[0])

    # If we have two supporting reasons, return them as two short sentences
    if len(supporting) >= 2:
        s1 = supporting[0][1]
        s2 = supporting[1][1]
        return f"{s1}. {s2}."

    # If we have one supporting and at least one opposing, return a combined sentence
    if len(supporting) == 1 and len(opposing) >= 1:
        opp = opposing[0][1]
        sup = supporting[0][1]
        return f"Despite {opp}, because {sup}."

    # Fallbacks: prefer one supporting + next best opposing or two top contributors
    if len(supporting) == 1:
        s1 = supporting[0][1]
        # try to find another contributor (opposing or neutral)
        if opposing:
            o1 = opposing[0][1]
            return f"Despite {o1}, because {s1}."
        return f"{s1}."

    # If no supporting reasons, pick top two opposing or available reasons across data
    combined = opposing[:2]
    if len(combined) >= 2:
        return f"Despite {combined[0][1]}, because {combined[1][1]}."

    if combined:
        return f"{combined[0][1]}."

    return "No concise reasons available."


def build_three_bullets(winner, reasoning_data):
    """Return up to three short bullet points (strings) summarizing key signals.
    Does not emit category headings; returns cleaned short phrases.
    """
    def clean(text):
        if not text:
            return ""
        return text.replace('—', ',').replace('*', '').strip()

    key = winner.lower()
    supporting = []  # (magnitude, text)
    opposing = []

    for q_idx, option_text, impacts, opt_obj in reasoning_data:
        if not impacts or key not in impacts:
            continue
        val = impacts.get(key, 0)
        reason_text = None
        if isinstance(opt_obj, dict):
            reason_text = opt_obj.get(f"reason_{key}")
        if not reason_text:
            reason_text = option_text

        reason_text = clean(reason_text)
        if not reason_text:
            continue

        if val > 0:
            supporting.append((val, reason_text))
        elif val < 0:
            opposing.append((abs(val), reason_text))

    supporting.sort(reverse=True, key=lambda x: x[0])
    opposing.sort(reverse=True, key=lambda x: x[0])

    bullets = []
    # prefer up to 3 supporting reasons
    for val, txt in supporting[:3]:
        bullets.append(txt)
    # if not enough, fill with opposing reasons
    if len(bullets) < 3:
        for val, txt in opposing[: (3 - len(bullets))]:
            bullets.append(txt)

    if not bullets:
        bullets = ["No strong indicators were recorded."]

    return bullets

# Render title
st.markdown("""
    <div class="title-container">
        <h1>🍲 FOOD CLASSIFIER 🥗 🥪</h1>
        <p>Answer questions about a food item to classify if it's more Soup, Salad, or Sandwich</p>
    </div>
""", unsafe_allow_html=True)

# Main layout
left, right = st.columns([2, 1])

# Right side: Live pie chart
with right:
    # Use a container rather than raw opening/closing HTML to avoid stray tags
    with st.container():
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown("### Live Classification")
        soup_pct, salad_pct, sandwich_pct = normalize_pcts(st.session_state.soup_pct, st.session_state.salad_pct, st.session_state.sandwich_pct)
        fig = create_pie_chart(soup_pct, salad_pct, sandwich_pct)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        breakdown = pd.DataFrame({
            'Category': ['SOUP', 'SALAD', 'SANDWICH'],
            'Percentage': [f'{soup_pct:.1f}%', f'{salad_pct:.1f}%', f'{sandwich_pct:.1f}%']
        })
        st.dataframe(breakdown, use_container_width=True, hide_index=True)
        # do not print raw closing tags

# Left side: Quiz flow
with left:
    if not st.session_state.quiz_started and not st.session_state.quiz_completed:
        st.markdown("""
            <div class="question-container">
                <h3>Ready to classify a food?</h3>
                <p>Think of any food item (pizza, ramen, caesar salad, burger, etc.) and answer 10 questions about its characteristics. The pie chart on the right updates as you answer.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Classification", use_container_width=True, key="start_btn"):
            st.session_state.quiz_started = True
            st.rerun()
    
    elif st.session_state.quiz_completed:
        soup_pct, salad_pct, sandwich_pct = normalize_pcts(st.session_state.soup_pct, st.session_state.salad_pct, st.session_state.sandwich_pct)
        winner, soup_reasons, salad_reasons, sandwich_reasons = get_winner_analysis(soup_pct, salad_pct, sandwich_pct, st.session_state.reasoning_data)
        
        percent_text = f"{soup_pct:.1f}%" if winner=="SOUP" else f"{salad_pct:.1f}%" if winner=="SALAD" else f"{sandwich_pct:.1f}%"
        st.markdown(f"""
            <div class="question-container">
                <h2>Classification Complete</h2>
                <h3>Result: {winner}</h3>
                
<p style="font-size: 1.2em; color: #667eea; font-weight: bold;">{percent_text}</p>

            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Why This Classification?")
        # Build and show exactly two concise reasons
        concise = build_two_reason_summary(winner, st.session_state.reasoning_data)
        st.markdown('<div class="question-container"><h4>Concise Reasons</h4></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="reasoning-box">{concise}</div>', unsafe_allow_html=True)
        
        # Show reasoning for each category
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="explanation-box"><h4>SOUP</h4></div>', unsafe_allow_html=True)
            if soup_reasons:
                for reason in soup_reasons[:3]:
                    r = reason.replace('—', ',').replace('*', '').strip()
                    st.markdown(f'<div class="reasoning-box">{r}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="reasoning-box">No strong soup indicators</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="explanation-box"><h4>SALAD</h4></div>', unsafe_allow_html=True)
            if salad_reasons:
                for reason in salad_reasons[:3]:
                    r = reason.replace('—', ',').replace('*', '').strip()
                    st.markdown(f'<div class="reasoning-box">{r}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="reasoning-box">No strong salad indicators</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="explanation-box"><h4>SANDWICH</h4></div>', unsafe_allow_html=True)
            if sandwich_reasons:
                for reason in sandwich_reasons[:3]:
                    r = reason.replace('—', ',').replace('*', '').strip()
                    st.markdown(f'<div class="reasoning-box">{r}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="reasoning-box">No strong sandwich indicators</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Classify Another Food", use_container_width=True, key="reset_btn"):
            st.session_state.current_question = 0
            st.session_state.soup_pct = 33.33
            st.session_state.salad_pct = 33.33
            st.session_state.sandwich_pct = 33.33
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.answers = {}
            st.session_state.reasoning_data = []
            st.rerun()
    
    else:
        # Quiz question display
        q_idx = st.session_state.current_question
        question = QUIZ_QUESTIONS[q_idx]
        
        progress_col1, progress_col2 = st.columns([1, 4])
        with progress_col1:
            st.metric("Question", f"{q_idx + 1}/10")
        with progress_col2:
            st.progress((q_idx) / len(QUIZ_QUESTIONS))
        
        st.markdown(f"""
            <div class="question-container">
                <div class="question-text">{question['question']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display options as a radio group + Next button to ensure single-click registration
        option_texts = [opt["text"] for opt in question["options"]]
        selected_text = st.radio("", option_texts, index=0, key=f"radio_{q_idx}")

        next_col, skip_col = st.columns([1, 1])
        with next_col:
            if st.button("Next", use_container_width=True, key=f"next_{q_idx}"):
                # find selected option
                selected_option = None
                for opt in question["options"]:
                    if opt["text"] == selected_text:
                        selected_option = opt
                        break

                if selected_option is None:
                    # safety fallback
                    selected_option = question["options"][0]

                # Update percentages with numeric impacts
                st.session_state.soup_pct += selected_option.get("soup", 0)
                st.session_state.salad_pct += selected_option.get("salad", 0)
                st.session_state.sandwich_pct += selected_option.get("sandwich", 0)

                # store reasoning entry: (question index, option text, impacts dict, option object)
                impacts = {
                    "soup": selected_option.get("soup", 0),
                    "salad": selected_option.get("salad", 0),
                    "sandwich": selected_option.get("sandwich", 0),
                }
                st.session_state.reasoning_data.append((q_idx, selected_option.get("text"), impacts, selected_option))
                st.session_state.answers[q_idx] = selected_option.get("text")

                # Move to next question
                st.session_state.current_question += 1
                if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                    st.session_state.quiz_completed = True

                st.rerun()

        with skip_col:
            if st.button("Skip", use_container_width=True, key=f"skip_{q_idx}"):
                # Move forward without changing scores (record skipped)
                st.session_state.reasoning_data.append((q_idx, "<skipped>", {"soup":0, "salad":0, "sandwich":0}, {}))
                st.session_state.current_question += 1
                if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                    st.session_state.quiz_completed = True
                st.rerun(