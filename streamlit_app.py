import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Soup vs Salad vs Sandwich",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for attractive styling with cool transitions
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Title styling */
    .title-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-in;
    }
    
    .title-container h1 {
        color: white;
        font-size: 3em;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        color: #e0e0e0;
        font-size: 1.2em;
        margin-top: 0.5rem;
    }
    
    /* Question card styling */
    .question-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        animation: slideIn 0.5s ease-out;
    }
    
    .question-text {
        font-size: 1.3em;
        font-weight: 600;
        color: #333;
        margin-bottom: 1.5rem;
    }
    
    /* Answer button styling with hover effects */
    .answer-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-size: 1em;
        cursor: pointer;
        margin: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .answer-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Results styling */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        animation: fadeIn 0.8s ease-in;
    }
    
    .result-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        animation: slideUp 0.6s ease-out;
    }
    
    .percentage-display {
        font-size: 2.5em;
        font-weight: bold;
        color: #667eea;
        margin: 1rem 0;
    }
    
    .explanation-text {
        background: #f0f2f6;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
        color: #444;
    }
    
    /* Progress bar */
    .progress-bar {
        height: 8px;
        background: #e0e0e0;
        border-radius: 10px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
    /* Emoji styling */
    .emoji-large {
        font-size: 4em;
        margin: 1rem 0;
        animation: bounce 0.6s ease-in-out;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.soup_score = 0
    st.session_state.salad_score = 0
    st.session_state.sandwich_score = 0
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False

# Define the quiz questions with their weightages for each category
# Format: {question, options: [{text, soup_weight, salad_weight, sandwich_weight}]}
QUIZ_QUESTIONS = [
    {
        "question": "🌡️ Do you prefer your food served hot or cold?",
        "options": [
            {"text": "Piping hot", "soup": 30, "salad": -10, "sandwich": 10},
            {"text": "Room temperature", "soup": 15, "salad": 15, "sandwich": 10},
            {"text": "Cold & refreshing", "soup": -20, "salad": 35, "sandwich": 15},
            {"text": "Temperature doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🍴 What's your preferred eating utensil?",
        "options": [
            {"text": "Spoon", "soup": 35, "salad": 10, "sandwich": -15},
            {"text": "Fork", "soup": 5, "salad": 40, "sandwich": 10},
            {"text": "Hands", "soup": -30, "salad": -20, "sandwich": 40},
            {"text": "Knife & Fork", "soup": 10, "salad": 25, "sandwich": 20},
        ]
    },
    {
        "question": "🥣 How soupy should your meal be?",
        "options": [
            {"text": "Very soupy/brothy", "soup": 40, "salad": -15, "sandwich": -10},
            {"text": "Some liquid content", "soup": 20, "salad": 5, "sandwich": 5},
            {"text": "Dry and crispy", "soup": -35, "salad": 30, "sandwich": 25},
            {"text": "It varies", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🌿 How much texture variety do you want?",
        "options": [
            {"text": "Smooth & consistent", "soup": 25, "salad": -10, "sandwich": 5},
            {"text": "Mixed textures", "soup": 15, "salad": 35, "sandwich": 20},
            {"text": "Crispy & crunchy", "soup": -15, "salad": 40, "sandwich": 25},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "⏱️ How long does your ideal meal take to eat?",
        "options": [
            {"text": "Quick & efficient (5-10 min)", "soup": 20, "salad": 5, "sandwich": 35},
            {"text": "Leisurely sipping (15-20 min)", "soup": 35, "salad": 10, "sandwich": 5},
            {"text": "Relaxed grazing (20+ min)", "soup": 10, "salad": 30, "sandwich": 15},
            {"text": "However long it takes", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🍅 How important is freshness of ingredients?",
        "options": [
            {"text": "Super important, fresh is best", "soup": 10, "salad": 40, "sandwich": 20},
            {"text": "Somewhat important", "soup": 15, "salad": 20, "sandwich": 20},
            {"text": "Not really, comfort counts more", "soup": 25, "salad": 5, "sandwich": 20},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🎨 Do you like customizing your food?",
        "options": [
            {"text": "Yes, lots of toppings & mix-ins", "soup": 15, "salad": 40, "sandwich": 35},
            {"text": "Some customization", "soup": 15, "salad": 15, "sandwich": 15},
            {"text": "Nah, keep it simple", "soup": 25, "salad": -10, "sandwich": 10},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🥘 Do you enjoy slurping/making noise while eating?",
        "options": [
            {"text": "YES! It's part of the fun", "soup": 35, "salad": -20, "sandwich": -15},
            {"text": "Sometimes", "soup": 15, "salad": 5, "sandwich": 5},
            {"text": "Prefer eating quietly", "soup": -15, "salad": 30, "sandwich": 20},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🧊 How important is temperature consistency?",
        "options": [
            {"text": "Stays hot throughout", "soup": 30, "salad": 5, "sandwich": 10},
            {"text": "Can be any temperature", "soup": 10, "salad": 15, "sandwich": 15},
            {"text": "Stays cold & crisp", "soup": -20, "salad": 35, "sandwich": 15},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🌟 How healthy should your meal be?",
        "options": [
            {"text": "Super healthy & nutritious", "soup": 10, "salad": 45, "sandwich": 10},
            {"text": "Reasonably healthy", "soup": 20, "salad": 25, "sandwich": 20},
            {"text": "Indulgent & comforting", "soup": 25, "salad": -15, "sandwich": 30},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "👥 How do you feel about eating with others?",
        "options": [
            {"text": "Love sharing a communal bowl", "soup": 35, "salad": 20, "sandwich": 10},
            {"text": "Can share but prefer individual", "soup": 15, "salad": 15, "sandwich": 15},
            {"text": "Prefer eating alone/my own portion", "soup": 5, "salad": 10, "sandwich": 25},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🌪️ What's your relationship with mess?",
        "options": [
            {"text": "Messy eating is fun", "soup": 20, "salad": -10, "sandwich": 5},
            {"text": "A little mess is okay", "soup": 15, "salad": 15, "sandwich": 20},
            {"text": "I prefer eating neat & clean", "soup": -10, "salad": 35, "sandwich": 30},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🌍 What's your eating style?",
        "options": [
            {"text": "Comfort food lover", "soup": 35, "salad": -10, "sandwich": 25},
            {"text": "Health-conscious", "soup": 10, "salad": 40, "sandwich": 15},
            {"text": "Quick & convenient", "soup": 5, "salad": 5, "sandwich": 35},
            {"text": "Adventurous & experimental", "soup": 15, "salad": 20, "sandwich": 15},
        ]
    },
    {
        "question": "❄️ How do you feel in different seasons?",
        "options": [
            {"text": "Love warm comfort in cold months", "soup": 40, "salad": -15, "sandwich": 15},
            {"text": "Love fresh & light in warm months", "soup": -20, "salad": 40, "sandwich": 10},
            {"text": "Same preferences year-round", "soup": 5, "salad": 5, "sandwich": 5},
            {"text": "Doesn't matter", "soup": 5, "salad": 5, "sandwich": 5},
        ]
    },
    {
        "question": "🎯 Pick your vibe!",
        "options": [
            {"text": "Cozy & warming", "soup": 40, "salad": 5, "sandwich": 10},
            {"text": "Fresh & energetic", "soup": -10, "salad": 45, "sandwich": 15},
            {"text": "Quick & satisfying", "soup": 10, "salad": 5, "sandwich": 40},
            {"text": "Mix of everything", "soup": 15, "salad": 15, "sandwich": 15},
        ]
    },
]

def render_title():
    """Render the main title section"""
    st.markdown("""
    <div class="title-container">
        <h1>🍲 SOUP vs SALAD vs SANDWICH 🥗🥪</h1>
        <p class="subtitle">Discover which food defines YOUR personality!</p>
    </div>
    """, unsafe_allow_html=True)

def render_question(question_num):
    """Render a single question"""
    question_data = QUIZ_QUESTIONS[question_num]
    
    # Progress bar
    progress = (question_num) / len(QUIZ_QUESTIONS)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Question", f"{question_num + 1}/{len(QUIZ_QUESTIONS)}")
    with col2:
        st.progress(progress)
    
    # Question
    st.markdown(f"""
    <div class="question-container">
        <div class="question-text">{question_data['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Options
    cols = st.columns(2)
    for idx, option in enumerate(question_data["options"]):
        with cols[idx % 2]:
            if st.button(option["text"], key=f"q{question_num}_o{idx}", use_container_width=True):
                # Update scores
                st.session_state.soup_score += option["soup"]
                st.session_state.salad_score += option["salad"]
                st.session_state.sandwich_score += option["sandwich"]
                
                # Move to next question
                st.session_state.current_question += 1
                
                if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                    st.session_state.quiz_completed = True
                
                st.rerun()

def calculate_percentages():
    """Calculate final percentages"""
    total = st.session_state.soup_score + st.session_state.salad_score + st.session_state.sandwich_score
    
    if total == 0:
        return 33.33, 33.33, 33.33
    
    soup_pct = (st.session_state.soup_score / total * 100) if total > 0 else 0
    salad_pct = (st.session_state.salad_score / total * 100) if total > 0 else 0
    sandwich_pct = (st.session_state.sandwich_score / total * 100) if total > 0 else 0
    
    # Handle negative scores
    soup_pct = max(0, soup_pct)
    salad_pct = max(0, salad_pct)
    sandwich_pct = max(0, sandwich_pct)
    
    # Normalize
    total_pct = soup_pct + salad_pct + sandwich_pct
    if total_pct > 0:
        soup_pct = (soup_pct / total_pct) * 100
        salad_pct = (salad_pct / total_pct) * 100
        sandwich_pct = (sandwich_pct / total_pct) * 100
    
    return soup_pct, salad_pct, sandwich_pct

def get_explanations(soup_pct, salad_pct, sandwich_pct):
    """Get explanations for each food type"""
    explanations = {
        "soup": {
            "title": "🍲 SOUP",
            "description": """
            You're a **Soup Person**! You value comfort, warmth, and the cozy feeling of a hearty meal. 
            You appreciate taking your time to savor flavors, don't mind a little mess, and love the communal 
            aspect of sharing a bowl. You're likely drawn to comfort and nostalgia, enjoying meals that feel like 
            a warm hug. Soups represent your preference for warmth, simplicity, and soul-satisfying nourishment.
            """
        },
        "salad": {
            "title": "🥗 SALAD",
            "description": """
            You're a **Salad Person**! You prioritize freshness, health, and variety in your meals. You love 
            customization and taking control of exactly what goes on your plate. You appreciate crispy textures, 
            clean eating, and meals that feel light and energizing. You're likely health-conscious, adventurous 
            with ingredients, and you believe eating should be both nourishing AND delicious.
            """
        },
        "sandwich": {
            "title": "🥪 SANDWICH",
            "description": """
            You're a **Sandwich Person**! You value efficiency, convenience, and practicality in your meals. 
            You appreciate eating with your hands, quick satisfaction, and the versatility of layering flavors. 
            You're likely someone who's always on the go, loves customization on-the-fly, and appreciates meals 
            that are straightforward and satisfying. Sandwiches represent your appreciation for simplicity and 
            effectiveness.
            """
        }
    }
    return explanations

def render_results():
    """Render results page"""
    soup_pct, salad_pct, sandwich_pct = calculate_percentages()
    
    # Find the winner
    percentages = {"🍲 SOUP": soup_pct, "🥗 SALAD": salad_pct, "🥪 SANDWICH": sandwich_pct}
    winner = max(percentages, key=percentages.get)
    winner_pct = percentages[winner]
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h2 style="margin-top: 0;">🎉 RESULTS 🎉</h2>
        <p style="font-size: 1.2em;">Here's what you are...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Results in columns
    col1, col2, col3 = st.columns(3)
    
    results_data = [
        ("🍲", "SOUP", soup_pct, "Warm & Comforting"),
        ("🥗", "SALAD", salad_pct, "Fresh & Healthy"),
        ("🥪", "SANDWICH", sandwich_pct, "Quick & Convenient"),
    ]
    
    colors = ["#FF6B6B", "#4ECDC4", "#FFE66D"]
    
    for col, (emoji, name, pct, subtitle) in zip([col1, col2, col3], results_data):
        with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {colors[results_data.index((emoji, name, pct, subtitle))]} 0%, 
            {colors[results_data.index((emoji, name, pct, subtitle))]}dd 100%); 
            border-radius: 12px; padding: 2rem; text-align: center; color: white;">
                <div style="font-size: 3em; margin: 1rem 0;">{emoji}</div>
                <div style="font-size: 1.5em; font-weight: bold; margin: 0.5rem 0;">{name}</div>
                <div style="font-size: 0.9em; margin-bottom: 1rem; opacity: 0.9;">{subtitle}</div>
                <div style="font-size: 2.5em; font-weight: bold;">{pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get explanations
    explanations = get_explanations(soup_pct, salad_pct, sandwich_pct)
    
    # Show detailed explanations
    st.markdown("### 📊 Detailed Breakdown")
    
    tabs = st.tabs(["🍲 Soup", "🥗 Salad", "🥪 Sandwich"])
    
    for tab, (food_type, exp_data) in zip(tabs, explanations.items()):
        with tab:
            col_left, col_right = st.columns([1, 2])
            
            with col_left:
                if food_type == "soup":
                    st.markdown(f"<div class='emoji-large'>🍲</div>", unsafe_allow_html=True)
                    pct_val = soup_pct
                elif food_type == "salad":
                    st.markdown(f"<div class='emoji-large'>🥗</div>", unsafe_allow_html=True)
                    pct_val = salad_pct
                else:
                    st.markdown(f"<div class='emoji-large'>🥪</div>", unsafe_allow_html=True)
                    pct_val = sandwich_pct
                
                st.markdown(f"<div class='percentage-display'>{pct_val:.1f}%</div>", unsafe_allow_html=True)
            
            with col_right:
                st.markdown(f"<div class='explanation-text'>{exp_data['description']}</div>", unsafe_allow_html=True)
    
    # Why sections for each food
    st.markdown("### 🤔 Why Each Food Got That Score")
    
    why_data = {
        "🍲 SOUP": {
            "high": ["You love warmth and comfort", "Preference for sipping & taking time", "Don't mind slurping", "Value communal eating"],
            "low": ["You prefer eating quickly", "Don't want hot liquids", "Prefer crispy textures", "Like eating with your hands"]
        },
        "🥗 SALAD": {
            "high": ["You prioritize health & freshness", "Love customization", "Prefer crispy textures", "Like eating neat & clean"],
            "low": ["You value comfort over health", "Prefer warm foods", "Don't like varying textures", "Would rather eat quickly"]
        },
        "🥪 SANDWICH": {
            "high": ["You prefer eating with your hands", "Want quick & convenient meals", "Like eating on-the-go", "Value simplicity"],
            "low": ["You prefer warm, liquid-based foods", "Take time to enjoy meals", "Don't like handling food", "Want complex flavor combinations"]
        }
    }
    
    col1, col2, col3 = st.columns(3)
    for col, (food, data) in zip([col1, col2, col3], why_data.items()):
        with col:
            st.markdown(f"**{food}**")
            st.markdown("**✅ Why it scored high:**")
            for reason in data["high"][:2]:
                st.markdown(f"• {reason}")
            st.markdown("**❌ Why it scored lower:**")
            for reason in data["low"][:2]:
                st.markdown(f"• {reason}")
    
    # Reset button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.current_question = 0
            st.session_state.soup_score = 0
            st.session_state.salad_score = 0
            st.session_state.sandwich_score = 0
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.rerun()

# Main app logic
render_title()

if not st.session_state.quiz_started and not st.session_state.quiz_completed:
    st.markdown("""
    <div class="question-container">
        <h3>Ready to find out your perfect food match? 🌟</h3>
        <p>Answer 15 quick questions about your eating preferences and we'll reveal whether you're 
        more of a <strong>Soup</strong>, <strong>Salad</strong>, or <strong>Sandwich</strong> person!</p>
        <p>This fun quiz analyzes your preferences for:</p>
        <ul>
            <li>🌡️ Temperature preferences</li>
            <li>🍴 Eating utensils</li>
            <li>🥒 Texture preferences</li>
            <li>⏱️ Eating speed & style</li>
            <li>🎨 Customization desires</li>
            <li>✨ And so much more!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 START THE QUIZ", use_container_width=True, key="start_button"):
            st.session_state.quiz_started = True
            st.rerun()

elif st.session_state.quiz_completed:
    render_results()

else:
    render_question(st.session_state.current_question)


