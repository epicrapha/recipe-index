import streamlit as st
import time
from infer import find_recipes

# Setup page config for a cleaner, modern look
st.set_page_config(
    page_title="Culinary Index",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for an Avant-Garde Minimalist Aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

/* Base Styles */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #050505;
    color: #E2E2E2;
}

/* Hide standard Streamlit elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Typography */
h1 {
    font-weight: 300 !important;
    letter-spacing: -0.05em;
    font-size: 3.5rem !important;
    color: #FFFFFF;
    margin-bottom: 2rem !important;
}

/* Input Fields */
div.stTextInput > div > div > input {
    background: #111111;
    border: 1px solid #2A2A2A;
    color: #FFF;
    border-radius: 12px;
    padding: 1.2rem;
    font-size: 1.1rem;
    font-weight: 300;
    transition: all 0.3s ease;
}
div.stTextInput > div > div > input:focus {
    border-color: #666;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
}

/* Glassmorphism Cards */
.recipe-card {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
}
.recipe-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.recipe-title {
    font-size: 1.6rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #FFF;
    letter-spacing: -0.02em;
}
.recipe-meta {
    font-size: 0.8rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.similarity-score {
    background: rgba(255,255,255,0.05);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    color: #A0A0A0;
}
.recipe-ingredients {
    font-weight: 300;
    color: #B0B0B0;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* UI Details */
.cluster-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 6px;
    background: #1A1A1A;
    border: 1px solid #333;
    font-size: 0.75rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 2rem;
}
.stExpander {
    background: transparent !important;
    border: none !important;
    border-top: 1px solid #222 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}
.stExpander summary {
    font-weight: 400 !important;
    color: #888 !important;
    letter-spacing: 0.05em;
    font-size: 0.9rem;
    padding: 1rem 0 !important;
}
.directions-text {
    color: #CCC;
    font-weight: 300;
    line-height: 1.8;
    font-size: 0.95rem;
    padding-bottom: 1rem;
}

/* Spinner adjustment */
.stSpinner > div > div {
    border-color: #333 !important;
    border-top-color: #FFF !important;
}
</style>
""", unsafe_allow_html=True)

# Main App UI
st.markdown("<h1>Culinary Index.</h1>", unsafe_allow_html=True)

# Minimal Input
query = st.text_input(
    label="Search",
    label_visibility="collapsed",
    placeholder="Enter ingredients e.g. chicken garlic soy sauce vinegar..."
)

if query:
    with st.spinner("Decoding flavor profiles..."):
        try:
            # We add a slight artificial delay purely for the "premium" feeling of processing
            time.sleep(0.4)
            result = find_recipes(query, top_n=5)
            
            # Show category badge
            st.markdown(f'<div class="cluster-badge">Topology: {result["cluster_label"]}</div>', unsafe_allow_html=True)
            
            # Render each card
            for index, recipe in enumerate(result["similar_recipes"]):
                score = recipe["similarity"] * 100
                title = recipe["title"]
                ingredients_list = ", ".join(recipe["ingredients"])
                
                # HTML template for the card
                card_html = f'''
                <div class="recipe-card">
                    <div class="recipe-title">{title}</div>
                    <div class="recipe-meta">
                        <span class="similarity-score">{score:.1f}% Match</span>
                    </div>
                    <div class="recipe-ingredients">
                        <strong style="color:#FFF;">Components:</strong><br/>
                        {ingredients_list}
                    </div>
                </div>
                '''
                st.markdown(card_html, unsafe_allow_html=True)
                
                # We place the expander immediately below natively to keep functionality
                with st.expander("Preparation Protocol"):
                    for step in recipe["directions"]:
                        st.markdown(f'<div class="directions-text">• {step}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("No valid flavor topology found. Try more common ingredients.")
