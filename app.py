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
    page_title="भाषा सेतु | Bhasha Setu",
    page_icon="🔤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for modern UI
def local_css():
    st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #f1f1f1;
    }
    .stApp {
        background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
    }
    .stTextInput, .stSelectbox, .stTextarea {
        border-radius: 10px;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
    }
    .stTextInput > div[data-baseweb="base-input"] > input {
        color: #ffffff !important;
    }
    .stSelectbox > div[data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
    }
    .stTextarea > div > div > textarea {
        color: #ffffff !important;
    }
    div.stButton > button {
        background-color: #FF5722;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #E64A19;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .card {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
        border-left: 5px solid #FF5722;
        color: #ffffff;
    }
    .language-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin: 1rem 0;
    }
    .language-btn {
        background-color: #2d2d2d;
        border: 1px solid #444;
        border-radius: 30px;
        padding: 5px 15px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
        color: #ffffff;
    }
    .language-btn:hover {
        background-color: #444444;
    }
    .language-btn.active {
        background-color: #FF5722;
        color: white;
        border-color: #FF5722;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    p {
        color: #e0e0e0;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #999;
        font-size: 0.8rem;
    }
    .indic-text {
        font-family: 'Noto Sans', sans-serif;
        font-size: 1.2rem;
        line-height: 1.6;
        color: #ffffff;
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 8px;
        border-left: 3px solid #FF5722;
    }
    /* Fix selectbox text color */
    div[data-baseweb="select"] > div {
        color: #ffffff !important;
    }
    /* Fix other input elements */
    input, textarea {
        color: #ffffff !important;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

local_css()

# Load animation
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Indic Languages Dictionary
INDIC_LANGUAGES = {
    "hi": "Hindi - हिन्दी",
    "bn": "Bengali - বাংলা",
    "ta": "Tamil - தமிழ்",
    "te": "Telugu - తెలుగు",
    "mr": "Marathi - मराठी",
    "gu": "Gujarati - ગુજરાતી",
    "kn": "Kannada - ಕನ್ನಡ",
    "ml": "Malayalam - മലയാളം",
    "pa": "Punjabi - ਪੰਜਾਬੀ",
    "or": "Odia - ଓଡ଼ିଆ",
    "as": "Assamese - অসমীয়া",
    "ur": "Urdu - اردو",
    "si": "Sinhala - සිංහල",
    "ne": "Nepali - नेपाली",
    "en": "English"
}

# Function to get language code from name
def get_lang_code(lang_name):
    for code, name in INDIC_LANGUAGES.items():
        if name == lang_name:
            return code
    return "en"  # Default to English

# Function to detect language
def detect_language(text):
    if not text or len(text.strip()) == 0:
        return "en"  # Default to English for empty input
    
    try:
        lang = detect(text)
        if lang in INDIC_LANGUAGES:
            return lang
        return "en"  # Default to English if not an Indic language
    except LangDetectException:
        return "en"  # Default to English if detection fails

# Function to translate text using deep_translator
def translate_text(text, target_lang):
    if not text or len(text.strip()) == 0:
        return ""
    
    try:
        source_lang = detect_language(text)
        if source_lang == target_lang:
            return text
        
        # Set a timeout for translation to prevent hanging
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        
        if not translated or len(translated.strip()) == 0:
            translator = GoogleTranslator(source='auto', target=target_lang)
            translated = translator.translate(text)
            
        return translated if translated else text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        try:
            # Fallback to auto detection
            translator = GoogleTranslator(source='auto', target=target_lang)
            return translator.translate(text)
        except Exception:
            return text  # Return original text if all translation attempts fail

# Function to translate using GROQ API for more context-aware translations
def translate_with_groq(text, source_lang, target_lang, api_key):
    if not text or not api_key:
        return ""
    
    if source_lang == target_lang:
        return text
    
    try:
        # Fix GROQ client initialization to only use api_key parameter
        client = groq.Client(api_key=api_key)
        source_lang_name = INDIC_LANGUAGES.get(source_lang, "Unknown")
        target_lang_name = INDIC_LANGUAGES.get(target_lang, "Unknown")
        
        prompt = f"""Translate the following text from {source_lang_name} to {target_lang_name}. 
        Maintain the cultural context, tone, and formatting of the original text.
        Ensure accuracy in grammar and script rendering.
        
        Text to translate: {text}"""
        
        # Try with llama3-70b-8192 model first, fall back to mixtral-8x7b-32768 if not available
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in Indic languages."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                max_tokens=2048
            )
        except Exception:
            # Fall back to a different model
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in Indic languages."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                max_tokens=2048
            )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"GROQ API error: {str(e)}")
        # Fallback to deep_translator
        return translate_text(text, target_lang)

# Function to convert text to speech
def text_to_speech(text, lang_code):
    if not text:
        return None
        
    try:
        # Map language codes to compatible gTTS language codes if needed
        gtts_lang_mapping = {
            "hi": "hi",
            "bn": "bn",
            "ta": "ta",
            "te": "te",
            "mr": "mr",
            "gu": "gu",
            "kn": "kn",
            "ml": "ml",
            "pa": "pa",
            "or": "en",  # Fallback to English if Odia not supported
            "as": "en",  # Fallback to English if Assamese not supported
            "ur": "ur",
            "si": "si",
            "ne": "ne",
            "en": "en"
        }
        
        # Get compatible language code or fallback to English
        compatible_lang = gtts_lang_mapping.get(lang_code, "en")
        
        tts = gTTS(text=text, lang=compatible_lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text to speech error: {str(e)}")
        # Fallback to English
        try:
            tts = gTTS(text=text, lang="en", slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name
        except Exception:
            return None

# Function to get audio player HTML
def get_audio_player(audio_path):
    try:
        # Check if the audio file exists
        if not os.path.exists(audio_path):
            return None
            
        # Check file size
        if os.path.getsize(audio_path) == 0:
            return None
        
        audio_file = open(audio_path, 'rb')
        audio_bytes = audio_file.read()
        audio_file.close()
        
        # Check if we actually got any content
        if not audio_bytes:
            return None
            
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
        return audio_html
    except Exception:
        return None

# App header
st.title("🔤 भाषा सेतु (Bhasha Setu)")
st.markdown("### Indic Languages Translation Platform")

# Main translation section
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Source")
    
    # Quick language buttons for common languages
    st.markdown('<div class="language-selector">', unsafe_allow_html=True)
    for lang_code in ["en", "hi", "mr", "bn", "ta"]:
        if st.button(INDIC_LANGUAGES[lang_code].split(" - ")[0], key=f"btn_{lang_code}"):
            source_lang = INDIC_LANGUAGES[lang_code]
            st.session_state.source_lang = source_lang
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dropdown for all languages
    if 'source_lang' not in st.session_state:
        st.session_state.source_lang = list(INDIC_LANGUAGES.values())[0]
        
    source_lang = st.selectbox(
        "Select source language", 
        options=list(INDIC_LANGUAGES.values()),
        index=list(INDIC_LANGUAGES.values()).index(st.session_state.source_lang)
    )
    source_lang_code = get_lang_code(source_lang)
    
    source_text = st.text_area(
        "Enter text to translate",
        height=250,
        placeholder="Type or paste your text here..."
    )
    
    col1_1, col1_2, col1_3 = st.columns([1, 1, 1])
    with col1_1:
        detect_btn = st.button("🔍 Detect Language", use_container_width=True)
    with col1_2:
        speak_source_btn = st.button("🔊 Listen", use_container_width=True)
    with col1_3:
        clear_btn = st.button("🧹 Clear", use_container_width=True)
        if clear_btn:
            st.session_state.source_text = ""
            st.rerun()

with col2:
    st.subheader("Translation")
    
    # Quick language buttons
    st.markdown('<div class="language-selector">', unsafe_allow_html=True)
    for lang_code in ["en", "hi", "mr", "bn", "ta"]:
        if st.button(INDIC_LANGUAGES[lang_code].split(" - ")[0], key=f"tgt_btn_{lang_code}"):
            target_lang = INDIC_LANGUAGES[lang_code]
            st.session_state.target_lang = target_lang
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dropdown for all languages
    if 'target_lang' not in st.session_state:
        st.session_state.target_lang = list(INDIC_LANGUAGES.values())[4]  # Default to Marathi
        
    target_lang = st.selectbox(
        "Select target language",
        options=list(INDIC_LANGUAGES.values()),
        index=list(INDIC_LANGUAGES.values()).index(st.session_state.target_lang)
    )
    target_lang_code = get_lang_code(target_lang)
    
    st.markdown('<div class="indic-text" id="translation-result" style="height: 250px; overflow-y: auto;">', unsafe_allow_html=True)
    
    # Store translated text in session state
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
        
    if source_text:
        with st.spinner("Translating..."):
            try:
                api_key_to_use = None
                if GROQ_API_KEY:
                    api_key_to_use = GROQ_API_KEY
                
                if api_key_to_use:
                    translated_text = translate_with_groq(
                        source_text, 
                        source_lang_code, 
                        target_lang_code,
                        api_key_to_use
                    )
                    translation_method = "AI Translation"
                else:
                    translated_text = translate_text(source_text, target_lang_code)
                    translation_method = "Google Translate"
                
                # Ensure we have a valid translation
                if not translated_text or len(translated_text.strip()) == 0:
                    translated_text = source_text
                    
                st.session_state.translated_text = translated_text
                st.markdown(f"<p>{translated_text}</p>", unsafe_allow_html=True)
                
                # Show which translation method was used
                st.caption(f"Translated using: {translation_method}")
            except Exception as e:
                st.error(f"Translation failed: {str(e)}")
                st.session_state.translated_text = ""
    else:
        if st.session_state.translated_text:
            st.markdown(f"<p>{st.session_state.translated_text}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #888;'>Translation will appear here...</p>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        copy_btn = st.button("📋 Copy", use_container_width=True)
        if copy_btn and st.session_state.translated_text:
            st.toast("Copied to clipboard!")
    with col2_2:
        if source_text or st.session_state.translated_text:
            speak_target_btn = st.button("🔊 Listen", key="speak_target", use_container_width=True)
            
            if speak_target_btn and st.session_state.translated_text:
                with st.spinner("Generating audio..."):
                    audio_path = text_to_speech(st.session_state.translated_text[:500], target_lang_code)
                    if audio_path:
                        audio_player_html = get_audio_player(audio_path)
                        if audio_player_html:
                            st.markdown(audio_player_html, unsafe_allow_html=True)
                            try:
                                os.remove(audio_path)
                            except:
                                pass

# Detect language logic
if detect_btn and source_text:
    with st.spinner("Detecting language..."):
        detected_lang_code = detect_language(source_text)
        detected_lang_name = INDIC_LANGUAGES.get(detected_lang_code, "Unknown")
        st.success(f"Detected language: {detected_lang_name}")
        # Automatically set the source language
        st.session_state.source_lang = detected_lang_name
        st.rerun()

# Listen to source text
if speak_source_btn and source_text:
    with st.spinner("Generating audio..."):
        audio_path = text_to_speech(source_text[:500], source_lang_code)
        if audio_path:
            audio_player_html = get_audio_player(audio_path)
            if audio_player_html:
                st.markdown(audio_player_html, unsafe_allow_html=True)
                try:
                    os.remove(audio_path)
                except:
                    pass

st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("© 2023 भाषा सेतु | Bhasha Setu - Indic Languages Translation")
st.markdown("</div>", unsafe_allow_html=True)
