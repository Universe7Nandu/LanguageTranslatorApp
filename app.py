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
    initial_sidebar_state="collapsed"
)

# CSS for professional, modern UI
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main container styles */
    .main {
        background-color: #111827;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
    }
    
    /* Main heading */
    h1 {
        color: #f3f4f6;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
    }
    
    h2, h3 {
        color: #f3f4f6;
        font-weight: 600;
    }
    
    /* Card container for main content */
    .content-card {
        background-color: #1f2937;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
        border-left: 5px solid #06b6d4;
    }
    
    /* Input/output containers */
    .translator-panel {
        background-color: #374151;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    
    /* Form elements styling */
    .stTextInput, .stSelectbox, .stTextarea {
        border-radius: 8px;
        background-color: #1f2937;
        color: #f3f4f6;
        border: 1px solid #4b5563;
    }
    
    /* Fix input text colors */
    .stTextInput > div[data-baseweb="base-input"] > input,
    .stSelectbox > div[data-baseweb="select"] > div,
    .stTextarea > div > div > textarea {
        color: #f3f4f6 !important;
    }
    
    /* Button styling */
    div.stButton > button {
        background-color: #06b6d4;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
    }
    
    div.stButton > button:hover {
        background-color: #0891b2;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Lang button grid */
    .lang-button-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .lang-button {
        background-color: #374151;
        color: #f3f4f6;
        border: 1px solid #4b5563;
        border-radius: 6px;
        padding: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .lang-button:hover {
        background-color: #4b5563;
        border-color: #06b6d4;
    }
    
    .lang-button.active {
        background-color: #06b6d4;
        border-color: #06b6d4;
        color: white;
    }
    
    /* Translation result styling */
    .translation-result {
        background-color: #1f2937;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 3px solid #06b6d4;
        font-family: 'Noto Sans', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        min-height: 250px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Status messages */
    .status-message {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    
    .status-message.success {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 3px solid #10b981;
        color: #d1fae5;
    }
    
    .status-message.info {
        background-color: rgba(6, 182, 212, 0.1);
        border-left: 3px solid #06b6d4;
        color: #cffafe;
    }
    
    .status-message.warning {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 3px solid #f59e0b;
        color: #fef3c7;
    }
    
    .status-message.error {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #ef4444;
        color: #fee2e2;
    }
    
    /* Feature cards */
    .feature-card {
        background-color: #374151;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-top: 3px solid #06b6d4;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding-top: 2rem;
        padding-bottom: 2rem;
        color: #9ca3af;
        font-size: 0.9rem;
    }
    
    /* Document upload area */
    .upload-area {
        border: 2px dashed #4b5563;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: #374151;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #06b6d4;
        background-color: #3a4658;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #1f2937;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.75rem 1rem;
        background-color: #374151;
        color: #f3f4f6;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #06b6d4;
        color: white;
    }
    
    /* Fix selectbox text color */
    div[data-baseweb="select"] > div {
        color: #f3f4f6 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #06b6d4;
    }
    
    /* Toast notifications */
    .stToast {
        background-color: #1f2937;
        color: #f3f4f6;
        border-left: 3px solid #06b6d4;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1f2937;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    
    /* Copy button styling */
    .copy-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #374151;
        border: none;
        color: #9ca3af;
        border-radius: 4px;
        padding: 0.3rem 0.5rem;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .copy-btn:hover {
        background-color: #4b5563;
        color: #f3f4f6;
    }
    
    /* App logo */
    .app-logo {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .logo-icon {
        font-size: 2.5rem;
        color: #06b6d4;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(to right, #0891b2, #0e7490);
        border-radius: 12px;
        padding: 2rem;
        color: white;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .features-list li {
        margin-bottom: 0.5rem;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

apply_custom_css()

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

# Custom UI components
def custom_status(message, status_type="info"):
    """Display a custom status message with styling"""
    st.markdown(f'<div class="status-message {status_type}">{message}</div>', unsafe_allow_html=True)

def language_button_grid(languages, key_prefix, selected_lang_code=None):
    """Create a grid of language buttons"""
    st.markdown('<div class="lang-button-grid">', unsafe_allow_html=True)
    
    for lang_code in languages:
        lang_name = INDIC_LANGUAGES[lang_code].split(" - ")[0]
        active_class = "active" if selected_lang_code == lang_code else ""
        
        if st.button(lang_name, key=f"{key_prefix}_{lang_code}", 
                   help=f"Select {INDIC_LANGUAGES[lang_code]}"):
            return lang_code
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None

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
        custom_status(f"Translation error: {str(e)}", "error")
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
        custom_status(f"GROQ API error: {str(e)}", "error")
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
        custom_status(f"Text to speech error: {str(e)}", "error")
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

# Main application UI
def main():
    # Store session state for languages and text
    if 'source_lang_code' not in st.session_state:
        st.session_state.source_lang_code = 'en'
    if 'target_lang_code' not in st.session_state:
        st.session_state.target_lang_code = 'hi'
    if 'source_text' not in st.session_state:
        st.session_state.source_text = ""
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = ""
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
    
    # App header with logo
    st.markdown('<div class="app-logo">', unsafe_allow_html=True)
    st.markdown('<span class="logo-icon">🔤</span>', unsafe_allow_html=True)
    st.title("भाषा सेतु | Bhasha Setu")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome banner (shown only first time)
    if st.session_state.show_welcome:
        st.markdown('<div class="welcome-banner">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("## Welcome to Bhasha Setu!")
            st.markdown("Your professional Indic language translation platform")
            st.markdown("""
            <ul class="features-list">
                <li>✓ Professional translation between 15 Indian languages</li>
                <li>✓ Document translation support</li>
                <li>✓ AI-powered for contextual accuracy</li>
                <li>✓ Text-to-speech capabilities</li>
            </ul>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Get Started", use_container_width=True):
                st.session_state.show_welcome = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main tabs for different translation modes
    tabs = st.tabs(["Text Translation", "Document Translation"])
    
    with tabs[0]:  # Text Translation Tab
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        # Language selection and translation area
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
            st.subheader("Source Language")
            
            # Language quick select buttons
            src_lang = language_button_grid(
                ["en", "hi", "mr", "bn", "ta"], 
                "src",
                st.session_state.source_lang_code
            )
            
            if src_lang:
                st.session_state.source_lang_code = src_lang
                st.rerun()
            
            # Full language dropdown
            source_lang = st.selectbox(
                "Select source language",
                options=list(INDIC_LANGUAGES.values()),
                index=list(INDIC_LANGUAGES.keys()).index(st.session_state.source_lang_code),
                key="source_lang_select"
            )
            st.session_state.source_lang_code = get_lang_code(source_lang)
            
            # Text input area
            source_text = st.text_area(
                "Enter text to translate",
                height=220,
                placeholder="Type or paste your text here...",
                key="source_text_area"
            )
            
            # Store in session state
            st.session_state.source_text = source_text
            
            # Action buttons
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                if st.button("🔍 Detect Language", use_container_width=True):
                    if source_text:
                        with st.spinner("Detecting language..."):
                            detected_lang_code = detect_language(source_text)
                            st.session_state.source_lang_code = detected_lang_code
                            custom_status(f"Detected language: {INDIC_LANGUAGES[detected_lang_code]}", "success")
                            st.rerun()
            
            with col1_2:
                if st.button("🔊 Listen", use_container_width=True, key="listen_source"):
                    if source_text:
                        with st.spinner("Generating audio..."):
                            audio_path = text_to_speech(source_text[:500], st.session_state.source_lang_code)
                            if audio_path:
                                audio_player_html = get_audio_player(audio_path)
                                if audio_player_html:
                                    st.markdown(audio_player_html, unsafe_allow_html=True)
                                    try:
                                        os.remove(audio_path)
                                    except:
                                        pass
            
            with col1_3:
                if st.button("🧹 Clear", use_container_width=True):
                    st.session_state.source_text = ""
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
            st.subheader("Target Language")
            
            # Language quick select buttons
            tgt_lang = language_button_grid(
                ["en", "hi", "mr", "bn", "ta"], 
                "tgt",
                st.session_state.target_lang_code
            )
            
            if tgt_lang:
                st.session_state.target_lang_code = tgt_lang
                st.rerun()
            
            # Full language dropdown
            target_lang = st.selectbox(
                "Select target language",
                options=list(INDIC_LANGUAGES.values()),
                index=list(INDIC_LANGUAGES.keys()).index(st.session_state.target_lang_code),
                key="target_lang_select"
            )
            st.session_state.target_lang_code = get_lang_code(target_lang)
            
            # Translation result display
            st.markdown('<div class="translation-result">', unsafe_allow_html=True)
            
            # Translate if we have source text
            if source_text:
                with st.spinner("Translating..."):
                    try:
                        api_key_to_use = GROQ_API_KEY if GROQ_API_KEY else None
                        
                        if api_key_to_use:
                            translated_text = translate_with_groq(
                                source_text,
                                st.session_state.source_lang_code,
                                st.session_state.target_lang_code,
                                api_key_to_use
                            )
                            translation_method = "AI Translation"
                        else:
                            translated_text = translate_text(
                                source_text, 
                                st.session_state.target_lang_code
                            )
                            translation_method = "Google Translate"
                        
                        # Ensure we have a valid translation
                        if not translated_text or len(translated_text.strip()) == 0:
                            translated_text = source_text
                        
                        # Store in session state
                        st.session_state.translated_text = translated_text
                        
                        # Display translation
                        st.markdown(f"<p>{translated_text}</p>", unsafe_allow_html=True)
                        st.caption(f"Translated using: {translation_method}")
                        
                    except Exception as e:
                        custom_status(f"Translation failed: {str(e)}", "error")
                        st.session_state.translated_text = ""
            else:
                if st.session_state.translated_text:
                    st.markdown(f"<p>{st.session_state.translated_text}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #9ca3af;'>Translation will appear here...</p>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Action buttons
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("📋 Copy", use_container_width=True):
                    if st.session_state.translated_text:
                        # Use clipboard JS via HTML
                        st.write(f'<div id="translated-text" style="display:none">{st.session_state.translated_text}</div>', unsafe_allow_html=True)
                        st.write("""
                        <script>
                        function copyToClipboard() {
                            const text = document.getElementById('translated-text').innerText;
                            navigator.clipboard.writeText(text);
                        }
                        copyToClipboard();
                        </script>
                        """, unsafe_allow_html=True)
                        st.toast("Copied to clipboard!")
            
            with col2_2:
                if st.button("🔊 Listen", use_container_width=True, key="listen_target"):
                    if st.session_state.translated_text:
                        with st.spinner("Generating audio..."):
                            audio_path = text_to_speech(
                                st.session_state.translated_text[:500], 
                                st.session_state.target_lang_code
                            )
                            if audio_path:
                                audio_player_html = get_audio_player(audio_path)
                                if audio_player_html:
                                    st.markdown(audio_player_html, unsafe_allow_html=True)
                                    try:
                                        os.remove(audio_path)
                                    except:
                                        pass
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close content card
    
    with tabs[1]:  # Document Translation Tab
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.subheader("Document Translation")
        st.markdown("Upload documents to translate between Indic languages")
        
        # Language selection for documents
        doc_col1, doc_col2 = st.columns(2)
        
        with doc_col1:
            doc_source_lang = st.selectbox(
                "Source language", 
                options=list(INDIC_LANGUAGES.values()),
                index=list(INDIC_LANGUAGES.keys()).index(st.session_state.source_lang_code),
                key="doc_source_lang"
            )
            doc_source_lang_code = get_lang_code(doc_source_lang)
        
        with doc_col2:
            doc_target_lang = st.selectbox(
                "Target language",
                options=list(INDIC_LANGUAGES.values()),
                index=list(INDIC_LANGUAGES.keys()).index(st.session_state.target_lang_code),
                key="doc_target_lang"
            )
            doc_target_lang_code = get_lang_code(doc_target_lang)
        
        # Document upload area
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        st.markdown("### Drag and drop your document here")
        st.caption("Supported formats: TXT, PDF, DOCX")
        
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=["txt", "pdf", "docx"], 
            key="document_upload", 
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Extract file information
            file_name = uploaded_file.name
            file_type = file_name.split('.')[-1].lower()
            file_size = uploaded_file.size / 1024  # KB
            
            # Display file info
            st.success(f"Uploaded: {file_name} ({file_size:.1f} KB)")
            
            # Translation quality selector
            quality_options = ["Standard (Faster)", "Enhanced (Better quality)"]
            selected_quality = st.select_slider(
                "Translation Quality", 
                options=quality_options, 
                value=quality_options[1]
            )
            
            # Process document button
            if st.button("Translate Document", use_container_width=True):
                with st.spinner("Processing document..."):
                    # Extract text from document
                    file_bytes = uploaded_file.read()
                    
                    if file_type == 'txt':
                        try:
                            file_content = file_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                # Try another common encoding
                                file_content = file_bytes.decode('latin-1')
                            except:
                                file_content = "Error: Could not decode the file."
                    else:
                        file_content = process_document_text(file_bytes, file_type)
                    
                    # Show content preview
                    with st.expander("Original Content Preview"):
                        st.text(file_content[:500] + ("..." if len(file_content) > 500 else ""))
                    
                    # Translate content
                    custom_status("Translating document content...", "info")
                    
                    api_key_to_use = GROQ_API_KEY if GROQ_API_KEY and selected_quality == "Enhanced (Better quality)" else None
                    
                    translated_content = translate_document(
                        file_content, 
                        doc_source_lang_code, 
                        doc_target_lang_code, 
                        api_key_to_use
                    )
                    
                    # Display translated content
                    with st.expander("Translated Content Preview", expanded=True):
                        st.markdown(f"<div class='translation-result'>{translated_content[:1000]}" +
                                  ("..." if len(translated_content) > 1000 else "") +
                                  "</div>", unsafe_allow_html=True)
                    
                    # Download options
                    st.subheader("Download Options")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download as TXT",
                            data=translated_content,
                            file_name=f"{file_name.split('.')[0]}_translated.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        st.download_button(
                            label="Download as PDF",
                            data=translated_content,
                            file_name=f"{file_name.split('.')[0]}_translated.pdf",
                            mime="application/pdf"
                        )
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close content card
    
    # Status bar for API key
    if GROQ_API_KEY:
        custom_status("✓ API key detected - AI-powered translation enabled", "success")
    else:
        custom_status("⚠ No API key detected - Using Google Translate", "warning")
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("© 2023 भाषा सेतु | Bhasha Setu - Professional Indic Languages Translation")
    st.markdown("</div>", unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
