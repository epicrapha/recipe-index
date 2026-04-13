import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import streamlit as st
import time
from infer import find_recipes

st.set_page_config(
    page_title="Culinary Index",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="auto"
)

# Initialize Session State Notebook
if "cookbook" not in st.session_state:
    st.session_state.cookbook = {}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: #050505;
    color: #E2E2E2;
}

#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

h1 {
    font-weight: 300 !important;
    letter-spacing: -0.05em;
    font-size: 3.5rem !important;
    color: #FFFFFF;
    margin-bottom: 1rem !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0A0A0A;
    border-right: 1px solid #1A1A1A;
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

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
    color: #888;
    font-weight: 400;
}
.stTabs [aria-selected="true"] {
    color: #FFF !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #FFF !important;
}

/* Glassmorphism Cards */
.recipe-card {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1rem;
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

/* Custom Checkbox */
.stCheckbox > div {
    font-weight: 300;
    color: #E2E2E2;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    background-color: #1A1A1A;
    border: 1px solid #333;
    color: #DDD;
    font-weight: 400;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    border-color: #FFF;
    color: #FFF;
}
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("<h1>Culinary Index.</h1>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### Settings")
    max_results = st.slider("Maximum Discoveries", min_value=1, max_value=10, value=5)
    st.markdown("---")
    st.markdown("Avant-Garde Architectural Deployment.")
    st.markdown(f"**Saved Recipes:** {len(st.session_state.cookbook)}")

# Main Tabs
tab1, tab2 = st.tabs(["🔍 Discovery", "📖 The Cookbook"])

with tab1:
    query = st.text_input(
        label="Search",
        label_visibility="collapsed",
        placeholder="Enter ingredients e.g. chicken garlic soy sauce vinegar..."
    )

    if query:
        with st.spinner("Decoding flavor profiles..."):
            try:
                time.sleep(0.4)
                result = find_recipes(query, top_n=max_results)
                
                st.markdown(f'<div class="cluster-badge">Topology: {result["cluster_label"]}</div>', unsafe_allow_html=True)
                
                for idx, recipe in enumerate(result["similar_recipes"]):
                    score = recipe["similarity"] * 100
                    title = recipe["title"]
                    ingredients_list = ", ".join(recipe["ingredients"])
                    
                    st.markdown(f'''
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
                    ''', unsafe_allow_html=True)
                    
                    # Layout row for operations
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        if title in st.session_state.cookbook:
                            st.button("Saved ✓", key=f"saved_{idx}", disabled=True)
                        else:
                            if st.button("Save Recipe", key=f"save_{idx}"):
                                st.session_state.cookbook[title] = recipe
                                st.rerun()

                    with col2:
                        with st.expander("Preparation Protocol"):
                            for step in recipe["directions"]:
                                st.markdown(f'<div style="color: #CCC; font-weight: 300; padding-bottom: 0.5rem;">• {step}</div>', unsafe_allow_html=True)
                    
                    st.write("") # Spacer

            except Exception as e:
                st.error("No valid flavor topology found. Try more common ingredients.")

with tab2:
    if not st.session_state.cookbook:
        st.markdown("<div style='text-align: center; color: #666; margin-top: 5rem;'>Your cookbook is empty.</div>", unsafe_allow_html=True)
    else:
        st.markdown("### Master Grocery List")
        
        # Aggregate Shopping List using parsed NER
        master_ingredients = set()
        for r_name, r_data in st.session_state.cookbook.items():
            for item in r_data["ingredients_ner"]:
                master_ingredients.add(item.lower())
                
        # Generate styled tags for groceries
        grocery_html = ""
        for item in sorted(master_ingredients):
            grocery_html += f'<span style="display:inline-block; background:rgba(255,255,255,0.05); border:1px solid #333; padding:0.4rem 0.8rem; border-radius:8px; margin:0.3rem; font-size:0.9rem; color:#DDD;">{item}</span>'
        st.markdown(f"<div style='margin-bottom: 3rem;'>{grocery_html}</div>", unsafe_allow_html=True)

        st.markdown("### Saved Formulations")
        for title, recipe in st.session_state.cookbook.items():
            st.markdown("---")
            col_t, col_b = st.columns([4, 1])
            with col_t:
                st.markdown(f"<h3 style='margin:0; font-weight:400;'>{title}</h3>", unsafe_allow_html=True)
            with col_b:
                if st.button("Remove", key=f"remove_{title}"):
                    del st.session_state.cookbook[title]
                    st.rerun()
            
            st.write(f"**Requires:** {', '.join(recipe['ingredients'])}")
            
            # Interactive Checklists for Cooking
            st.markdown("<br/>**Preparation:**", unsafe_allow_html=True)
            for s_idx, step in enumerate(recipe["directions"]):
                # Create a unique, deterministic key for each checkbox
                st.checkbox(step, key=f"chk_{hash(title)}_{s_idx}")
