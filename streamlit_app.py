import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Food Classifier - SSS",
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
    
    /* Results styling */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        animation: fadeIn 0.8s ease-in;
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.soup_pct = 33.33
    st.session_state.salad_pct = 33.33
    st.session_state.sandwich_pct = 33.33
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False
    st.session_state.food_name = ""
    st.session_state.answers = {}

# Define the quiz questions about food characteristics
# Each answer affects the three percentages
QUIZ_QUESTIONS = [
    {
        "question": "💧 How much liquid content does this food have?",
        "options": [
            {"text": "Very high - mostly liquid/broth", "soup": +20, "salad": -10, "sandwich": -15},
            {"text": "Moderate - some liquid", "soup": +10, "salad": 0, "sandwich": -5},
            {"text": "Low - mostly dry", "soup": -15, "salad": +15, "sandwich": +10},
            {"text": "No liquid", "soup": -20, "salad": +20, "sandwich": +15},
        ]
    },
    {
        "question": "🌡️ What temperature is it typically served at?",
        "options": [
            {"text": "Hot/steaming", "soup": +20, "salad": -15, "sandwich": 0},
            {"text": "Warm", "soup": +10, "salad": -5, "sandwich": +5},
            {"text": "Room temperature", "soup": -5, "salad": +5, "sandwich": +5},
            {"text": "Cold/chilled", "soup": -20, "salad": +20, "sandwich": +5},
        ]
    },
    {
        "question": "🍴 How is it typically eaten?",
        "options": [
            {"text": "With a spoon, sipped/slurped", "soup": +25, "salad": -10, "sandwich": -20},
            {"text": "With a fork", "soup": -5, "salad": +25, "sandwich": -10},
            {"text": "With hands/fingers", "soup": -15, "salad": -5, "sandwich": +30},
            {"text": "With knife & fork", "soup": -5, "salad": +15, "sandwich": +5},
        ]
    },
    {
        "question": "🥬 What's the main component?",
        "options": [
            {"text": "Broth, stock, or liquid base", "soup": +30, "salad": -15, "sandwich": -20},
            {"text": "Fresh vegetables & greens", "soup": -10, "salad": +30, "sandwich": -5},
            {"text": "Bread, meat, cheese between bread", "soup": -20, "salad": -10, "sandwich": +35},
            {"text": "Mix of everything", "soup": 0, "salad": 0, "sandwich": 0},
        ]
    },
    {
        "question": "📦 What's the primary container/serving vessel?",
        "options": [
            {"text": "Bowl or cup", "soup": +25, "salad": +5, "sandwich": -15},
            {"text": "Plate", "soup": -10, "salad": +20, "sandwich": +5},
            {"text": "In/on bread or hand-held", "soup": -20, "salad": -5, "sandwich": +30},
            {"text": "Doesn't matter/flexible", "soup": 0, "salad": 0, "sandwich": 0},
        ]
    },
    {
        "question": "🥘 How much solid matter vs liquid?",
        "options": [
            {"text": "Mostly liquid with bits in it", "soup": +20, "salad": -15, "sandwich": -15},
            {"text": "Balanced - equal solids and liquid", "soup": +5, "salad": +5, "sandwich": 0},
            {"text": "Mostly solid pieces", "soup": -15, "salad": +15, "sandwich": +5},
            {"text": "100% solid/dry - no liquid", "soup": -25, "salad": +20, "sandwich": +15},
        ]
    },
    {
        "question": "🌿 How much texture variety?",
        "options": [
            {"text": "Smooth & consistent (creamy)", "soup": +15, "salad": -10, "sandwich": -5},
            {"text": "Varied textures - crunchy & soft", "soup": -5, "salad": +25, "sandwich": +10},
            {"text": "Multiple layers & textures", "soup": -5, "salad": +10, "sandwich": +20},
            {"text": "Uniform texture", "soup": +10, "salad": -10, "sandwich": 0},
        ]
    },
    {
        "question": "⏱️ How long does it take to eat?",
        "options": [
            {"text": "Fast - under 5 minutes", "soup": -10, "salad": -10, "sandwich": +25},
            {"text": "5-10 minutes", "soup": +5, "salad": +5, "sandwich": +15},
            {"text": "10-20 minutes (leisurely sipping)", "soup": +20, "salad": +10, "sandwich": -5},
            {"text": "20+ minutes (prolonged eating)", "soup": +10, "salad": +20, "sandwich": -10},
        ]
    },
    {
        "question": "🧅 How many distinct ingredients/components?",
        "options": [
            {"text": "Few (1-3 main ingredients)", "soup": +15, "salad": -10, "sandwich": +10},
            {"text": "Several (4-6 ingredients)", "soup": +5, "salad": +10, "sandwich": +10},
            {"text": "Many (7+ ingredients)", "soup": -5, "salad": +20, "sandwich": +10},
            {"text": "Infinite variations possible", "soup": 0, "salad": +15, "sandwich": +20},
        ]
    },
    {
        "question": "🧴 Is there a binding/sauce element?",
        "options": [
            {"text": "Yes - broth or liquid base", "soup": +25, "salad": -10, "sandwich": -5},
            {"text": "Yes - creamy dressing/sauce", "soup": +10, "salad": +15, "sandwich": +5},
            {"text": "Light or no sauce", "soup": -15, "salad": +20, "sandwich": +10},
            {"text": "None", "soup": -20, "salad": +10, "sandwich": +20},
        ]
    },
    {
        "question": "🔥 Can it get cold and still be itself?",
        "options": [
            {"text": "No - it's ruined cold", "soup": +20, "salad": -15, "sandwich": +5},
            {"text": "Somewhat - still okay but different", "soup": +10, "salad": +5, "sandwich": +10},
            {"text": "Yes - just as good cold", "soup": -15, "salad": +25, "sandwich": +10},
            {"text": "Better cold", "soup": -25, "salad": +30, "sandwich": +5},
        ]
    },
    {
        "question": "👃 Does it have a strong, aromatic scent?",
        "options": [
            {"text": "Yes - very aromatic & warming", "soup": +15, "salad": -5, "sandwich": -10},
            {"text": "Moderately aromatic", "soup": +5, "salad": +5, "sandwich": +5},
            {"text": "Light or subtle aroma", "soup": -5, "salad": +15, "sandwich": +10},
            {"text": "Not aromatic", "soup": -10, "salad": +10, "sandwich": +10},
        ]
    },
    {
        "question": "🤲 Is it messy to eat?",
        "options": [
            {"text": "Very messy", "soup": +15, "salad": -5, "sandwich": 0},
            {"text": "Moderately messy", "soup": +10, "salad": +5, "sandwich": +5},
            {"text": "Relatively clean", "soup": -5, "salad": +15, "sandwich": +10},
            {"text": "Very clean/neat", "soup": -15, "salad": +20, "sandwich": +15},
        ]
    },
    {
        "question": "🎯 Primary eating context?",
        "options": [
            {"text": "Comfort/warming meal", "soup": +20, "salad": -10, "sandwich": +5},
            {"text": "Healthy option", "soup": -5, "salad": +25, "sandwich": 0},
            {"text": "Quick/convenient grab", "soup": -15, "salad": 0, "sandwich": +30},
            {"text": "Customizable experience", "soup": 0, "salad": +20, "sandwich": +15},
        ]
    },
]

def render_title():
    """Render the main title section"""
    st.markdown("""
    <div class="title-container">
        <h1>🍲 FOOD CLASSIFIER 🥗🥪</h1>
        <p class="subtitle">Is your food a Soup, Salad, or Sandwich?</p>
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
                # Update percentages based on the adjustment values
                adjustment = option
                total_adjustment = adjustment["soup"] + adjustment["salad"] + adjustment["sandwich"]
                
                # Apply the adjustments
                st.session_state.soup_pct += adjustment["soup"]
                st.session_state.salad_pct += adjustment["salad"]
                st.session_state.sandwich_pct += adjustment["sandwich"]
                
                # Ensure no negative percentages and normalize
                st.session_state.soup_pct = max(0, st.session_state.soup_pct)
                st.session_state.salad_pct = max(0, st.session_state.salad_pct)
                st.session_state.sandwich_pct = max(0, st.session_state.sandwich_pct)
                
                # Normalize to 100
                total = st.session_state.soup_pct + st.session_state.salad_pct + st.session_state.sandwich_pct
                if total > 0:
                    st.session_state.soup_pct = (st.session_state.soup_pct / total) * 100
                    st.session_state.salad_pct = (st.session_state.salad_pct / total) * 100
                    st.session_state.sandwich_pct = (st.session_state.sandwich_pct / total) * 100
                
                st.session_state.answers[question_num] = option["text"]
                
                # Move to next question
                st.session_state.current_question += 1
                
                if st.session_state.current_question >= len(QUIZ_QUESTIONS):
                    st.session_state.quiz_completed = True
                
                st.rerun()

def create_pie_chart():
    """Create an animated pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=['🍲 SOUP', '🥗 SALAD', '🥪 SANDWICH'],
        values=[st.session_state.soup_pct, st.session_state.salad_pct, st.session_state.sandwich_pct],
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFE66D']),
        textinfo='label+percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
        textfont=dict(size=14, color='white'),
        marker_line=dict(color='white', width=2)
    )])
    
    fig.update_layout(
        showlegend=True,
        height=500,
        font=dict(size=16),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def get_winner_description():
    """Get description based on winning category"""
    percentages = {
        "soup": st.session_state.soup_pct,
        "salad": st.session_state.salad_pct,
        "sandwich": st.session_state.sandwich_pct
    }
    
    winner = max(percentages, key=percentages.get)
    
    descriptions = {
        "soup": {
            "title": "🍲 This is SOUP!",
            "emoji": "🍲",
            "description": "This food has the characteristics of a **classic soup**. It's likely liquid-based, warm, comforting, and meant to be sipped or spooned. Think broth, stew, ramen, or chowder!",
            "characteristics": [
                "✓ Contains significant liquid/broth",
                "✓ Served hot or warm",
                "✓ Eaten with a spoon",
                "✓ Aromatic and warming",
                "✓ Takes time to enjoy"
            ]
        },
        "salad": {
            "title": "🥗 This is SALAD!",
            "emoji": "🥗",
            "description": "This food has the characteristics of a **fresh salad**. It's likely crisp, fresh, customizable, and meant to be eaten with a fork or hands. Think greens, grain bowls, or ceviche!",
            "characteristics": [
                "✓ Fresh, crisp components",
                "✓ Served cold or room temperature",
                "✓ Eaten with a fork or hands",
                "✓ Multiple varied ingredients",
                "✓ Healthy and light"
            ]
        },
        "sandwich": {
            "title": "🥪 This is SANDWICH!",
            "emoji": "🥪",
            "description": "This food has the characteristics of a **sandwich**. It's likely portable, quick to eat, hand-held, and features layers of bread and fillings. Think sandwiches, wraps, tacos, or burgers!",
            "characteristics": [
                "✓ Bread-based or hand-held",
                "✓ Eaten quickly",
                "✓ Portable and convenient",
                "✓ Eaten with hands",
                "✓ Customizable layers"
            ]
        }
    }
    
    return descriptions[winner]

def render_results():
    """Render results page with pie chart"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h2 style="margin-top: 0;">✨ FOOD CLASSIFICATION RESULTS ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Display pie chart
    fig = create_pie_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Get winner info
    winner_info = get_winner_description()
    
    # Display winner
    st.markdown(f"""
    <div class="results-container">
        <h2 style="text-align: center; margin-top: 0;">{winner_info['title']}</h2>
        <p style="font-size: 1.1em; line-height: 1.6;">{winner_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display characteristics
    st.markdown("### 🎯 Key Characteristics:")
    col1, col2, col3 = st.columns(3)
    
    for idx, char in enumerate(winner_info['characteristics']):
        if idx < 2:
            col1.markdown(char)
        elif idx < 4:
            col2.markdown(char)
        else:
            col3.markdown(char)
    
    # Display breakdown
    st.markdown("---")
    st.markdown("### 📊 Complete Breakdown:")
    
    breakdown_data = {
        'Category': ['SOUP', 'SALAD', 'SANDWICH'],
        'Percentage': [f"{st.session_state.soup_pct:.1f}%", 
                       f"{st.session_state.salad_pct:.1f}%", 
                       f"{st.session_state.sandwich_pct:.1f}%"],
    }
    
    df = pd.DataFrame(breakdown_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Show reasoning
    st.markdown("### 💡 How We Classified It:")
    
    reason_cols = st.columns(3)
    
    if st.session_state.soup_pct > 30:
        with reason_cols[0]:
            st.markdown(f"""
            **🍲 SOUP ({st.session_state.soup_pct:.1f}%)**
            
            Strong liquid content, warm temperature, and spoon-eating indicate soup characteristics.
            """)
    else:
        with reason_cols[0]:
            st.markdown(f"**🍲 SOUP ({st.session_state.soup_pct:.1f}%)**\n\nLess soup-like characteristics.")
    
    if st.session_state.salad_pct > 30:
        with reason_cols[1]:
            st.markdown(f"""
            **🥗 SALAD ({st.session_state.salad_pct:.1f}%)**
            
            Fresh ingredients, cold temperature, and varied textures indicate salad characteristics.
            """)
    else:
        with reason_cols[1]:
            st.markdown(f"**🥗 SALAD ({st.session_state.salad_pct:.1f}%)**\n\nLess salad-like characteristics.")
    
    if st.session_state.sandwich_pct > 30:
        with reason_cols[2]:
            st.markdown(f"""
            **🥪 SANDWICH ({st.session_state.sandwich_pct:.1f}%)**
            
            Bread-based, hand-held, and quick to eat indicate sandwich characteristics.
            """)
    else:
        with reason_cols[2]:
            st.markdown(f"**🥪 SANDWICH ({st.session_state.sandwich_pct:.1f}%)**\n\nLess sandwich-like characteristics.")
    
    # Reset button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Classify Another Food", use_container_width=True):
            st.session_state.current_question = 0
            st.session_state.soup_pct = 33.33
            st.session_state.salad_pct = 33.33
            st.session_state.sandwich_pct = 33.33
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.food_name = ""
            st.session_state.answers = {}
            st.rerun()

# Main app logic
render_title()

if not st.session_state.quiz_started and not st.session_state.quiz_completed:
    # Welcome screen
    st.markdown("""
    <div class="question-container">
        <h3>🎯 What is this food?</h3>
        <p>Thinking about a specific food? Tell us what it is, and we'll classify whether it's more of a 
        <strong>Soup</strong>, <strong>Salad</strong>, or <strong>Sandwich</strong> based on its characteristics!</p>
        <p>We'll ask you 14 questions about:</p>
        <ul>
            <li>💧 Liquid content</li>
            <li>🌡️ Temperature</li>
            <li>🍴 How it's eaten</li>
            <li>🥬 Main components</li>
            <li>📦 Serving vessel</li>
            <li>🧅 Number of ingredients</li>
            <li>✨ And more!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Input for food name
    st.markdown("### What food are we classifying?")
    food_input = st.text_input("Enter the name of the food:", placeholder="e.g., Pizza, Pasta, Burrito, Greek Salad...")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 START CLASSIFICATION", use_container_width=True, key="start_button"):
            if food_input.strip():
                st.session_state.food_name = food_input
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("Please enter a food name!")

elif st.session_state.quiz_completed:
    render_results()

else:
    # Display current food being classified
    st.markdown(f"### Classifying: **{st.session_state.food_name}**")
    
    render_question(st.session_state.current_question)


