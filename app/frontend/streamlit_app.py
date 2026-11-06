import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Pointing to your live Render backend
BACKEND_URL = os.getenv("BACKEND_URL", "https://social-and-script-idea-generator.onrender.com").rstrip("/")
GENERATE_URL = f"{BACKEND_URL}/api/generate"

st.set_page_config(page_title="AI Social Media Generator", page_icon="✦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 3rem; max-width: 900px; }
.main-title { font-size: 28px; font-weight: 700; color: #1E293B; margin-bottom: 30px; text-align: center; }
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.stTextInput label, .stSelectbox label, .stNumberInput label { font-size: 14px !important; font-weight: 500 !important; color: #334155 !important; }
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input { background-color: #F8FAFC !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; min-height: 44px; font-size: 14px !important; }
.stButton button[kind="primary"] { background-color: #0F172A !important; color: #FFFFFF !important; border-radius: 8px !important; width: 100% !important; font-weight: 600 !important; }
.stButton button[kind="primary"]:hover { background-color: #1E293B !important; }
.footer-text { text-align: center; color: #94A3B8; font-size: 13px; margin-top: 40px; border-top: 1px solid #E2E8F0; padding-top: 20px; }
.output-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">✨ AI Social Media Content Generator</div>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1: topic = st.text_input("Topic / Niche", placeholder="e.g., AI productivity tips")
    with col2: audience = st.text_input("Target Audience", placeholder="e.g., developers, students")

    st.write("")
    col3, col4 = st.columns(2)
    with col3: platform = st.selectbox("Publishing Platform", ["Instagram", "YouTube", "LinkedIn", "Twitter/X", "Facebook", "TikTok"])
    with col4: content_format = st.selectbox("Content Format", ["💡 Content Ideas", "📝 Captions + Hashtags", "🎬 Full Video Script", "🎣 Opening Hook", "🚀 CTA Only"])

    st.write("")
    col5, col6 = st.columns(2)
    with col5: 
        tone = st.selectbox("Tone of Voice", ["Professional", "Casual", "Witty", "Inspirational", "Educational"])
    with col6:
        num_recs = st.number_input("Number of Recommendations", min_value=1, max_value=10, value=3, step=1)

    st.write("")
    generate_clicked = st.button("✨ Generate Content", type="primary")

if generate_clicked:
    if not topic.strip() or not audience.strip():
        st.warning("Please fill in both Topic and Audience.")
    else:
        format_mapping = {
            "💡 Content Ideas": "ideas",
            "📝 Captions + Hashtags": "captions",
            "🎬 Full Video Script": "script",
            "🎣 Opening Hook": "hooks",
            "🚀 CTA Only": "cta"
        }
        backend_content_type = format_mapping.get(content_format, "ideas")

        payload = {
            "topic": topic,
            "platform": platform,
            "audience": audience,
            "tone": tone,
            "content_type": backend_content_type,
            "num_recommendations": num_recs, # Added to payload
            "use_rag": True
        }

        with st.spinner("Generating content... (First request may take 20s to wake up Render)"):
            try:
                response = requests.post(GENERATE_URL, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
                
                # Your backend returns 'content', not 'result'
                content = data.get("content", "")
                
                if not content.strip():
                    st.error("The AI returned empty content. Please try again.")
                else:
                    st.success("Content generated successfully!")
                    st.markdown("### Generated Content")
                    st.markdown(content) 
                    st.write("")
                    st.download_button("⬇ Download Output", data=content, file_name=f"{platform.lower()}_content.md", mime="text/markdown")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Render might be asleep or restarting. Please wait 30 seconds and try again.")
            except requests.HTTPError as e:
                st.error(f"API Error: {e.response.status_code}")
                st.code(e.response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown('<div class="footer-text">Developed by Suhana | Kavyasri | Veermani | Rishitha | Charan</div>', unsafe_allow_html=True)
