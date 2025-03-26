import os
import base64
import tempfile
import streamlit as st
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import groq
from gtts import gTTS
from PIL import Image
import requests
from langdetect import detect, LangDetectException

# Load environment variables from .env file
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Simple Language Translator",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --bg-color: #1a1a1a;
        --card-bg: #2d2d2d;
        --accent: #4CAF50;
        --text: #ffffff;
        --text-secondary: #b0b0b0;
    }

    /* Main container */
    .main {
        background-color: var(--bg-color);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--bg-color);
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--text);
        font-weight: 600;
    }

    /* Translation panels */
    .translator-panel {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #404040;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }

    .stButton > button:hover {
        background-color: #45a049 !important;
        border: none !important;
    }

    /* Text areas and inputs */
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #363636 !important;
        color: var(--text) !important;
        border: 1px solid #404040 !important;
    }

    /* Status messages */
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }

    .status-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--accent);
    }

    .status-error {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid #f44336;
    }

    /* Audio player */
    audio {
        width: 100%;
        margin-top: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Language dictionary
LANGUAGES = {
    "en": "English",
    "hi": "Hindi - हिन्दी",
    "mr": "Marathi - मराठी",
    "bn": "Bengali - বাংলা",
    "ta": "Tamil - தமிழ்",
    "te": "Telugu - తెలుగు",
    "gu": "Gujarati - ગુજરાતી",
    "kn": "Kannada - ಕನ್ನಡ",
    "ml": "Malayalam - മലയാളം",
    "pa": "Punjabi - ਪੰਜਾਬੀ",
    "ur": "Urdu - اردو"
}

def translate_text(text, target_lang, source_lang='auto'):
    """Translate text using Google Translator"""
    try:
        if not text:
            return ""
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return ""

def text_to_speech(text, lang_code):
    """Convert text to speech"""
    try:
        if not text:
            return None
        
        # Map language codes for gTTS
        gtts_lang_mapping = {
            "hi": "hi", "bn": "bn", "ta": "ta",
            "te": "te", "mr": "mr", "gu": "gu",
            "kn": "kn", "ml": "ml", "pa": "pa",
            "ur": "ur", "en": "en"
        }
        
        lang = gtts_lang_mapping.get(lang_code, "en")
        tts = gTTS(text=text, lang=lang, slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def get_audio_player(audio_path):
    """Generate HTML for audio player"""
    try:
        if not os.path.exists(audio_path):
            return None
        
        audio_file = open(audio_path, 'rb')
        audio_bytes = audio_file.read()
        audio_file.close()
        
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return f"""
            <audio controls>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
    except Exception:
        return None

def main():
    # App header
    st.title("🌐 Simple Language Translator")
    st.markdown("Translate text between multiple languages easily")

    # Main translation interface
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
        source_lang = st.selectbox(
            "From",
            options=list(LANGUAGES.values()),
            index=0,
            key="source_lang"
        )
        
        source_text = st.text_area(
            "Enter text to translate",
            height=200,
            placeholder="Type or paste your text here...",
            key="source_text"
        )

        # Source language controls
        if st.button("🔊 Listen to Source Text", use_container_width=True):
            if source_text:
                source_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(source_lang)]
                audio_path = text_to_speech(source_text, source_lang_code)
                if audio_path:
                    audio_player = get_audio_player(audio_path)
                    if audio_player:
                        st.markdown(audio_player, unsafe_allow_html=True)
                        try:
                            os.remove(audio_path)
                        except:
                            pass

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
        target_lang = st.selectbox(
            "To",
            options=list(LANGUAGES.values()),
            index=1,
            key="target_lang"
        )

        # Translation
        if source_text:
            source_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(source_lang)]
            target_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(target_lang)]
            
            translated_text = translate_text(source_text, target_lang_code, source_lang_code)
            
            if translated_text:
                st.text_area(
                    "Translation",
                    value=translated_text,
                    height=200,
                    key="translated_text"
                )

                # Target language controls
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔊 Listen to Translation", use_container_width=True):
                        audio_path = text_to_speech(translated_text, target_lang_code)
                        if audio_path:
                            audio_player = get_audio_player(audio_path)
                            if audio_player:
                                st.markdown(audio_player, unsafe_allow_html=True)
                                try:
                                    os.remove(audio_path)
                                except:
                                    pass
                
                with col2:
                    if st.button("📋 Copy Translation", use_container_width=True):
                        st.code(translated_text)
                        st.success("Text copied to clipboard!")

        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made with ❤️ | Simple Language Translator"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
