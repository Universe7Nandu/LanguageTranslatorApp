import streamlit as st
import pandas as pd
import requests
import io
import base64
from gtts import gTTS
import tempfile
import os
from PIL import Image
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import groq
import json
import time
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import streamlit_toggle as tog
from streamlit_extras.stateful_button import button
from streamlit_extras.stylable_container import stylable_container
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
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
        background-color: #f5f5f5;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
    }
    .stTextInput, .stSelectbox, .stTextarea {
        border-radius: 10px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
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
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .language-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin: 1rem 0;
    }
    .language-btn {
        background-color: #f0f0f0;
        border: 1px solid #e0e0e0;
        border-radius: 30px;
        padding: 5px 15px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .language-btn:hover {
        background-color: #e0e0e0;
    }
    .language-btn.active {
        background-color: #FF5722;
        color: white;
        border-color: #FF5722;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #FFFFFF;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5722;
        color: white;
    }
    h1, h2, h3 {
        color: #333;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #666;
        font-size: 0.8rem;
    }
    .indic-text {
        font-family: 'Noto Sans', sans-serif;
        font-size: 1.2rem;
        line-height: 1.6;
    }
    .custom-info-box {
        background-color: #e8f4f8;
        border-left: 4px solid #4abde8;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .custom-success-box {
        background-color: #e8f8e9;
        border-left: 4px solid #4ae86b;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .custom-warning-box {
        background-color: #fff8e8;
        border-left: 4px solid #e8c44a;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .developer-profile {
        display: flex;
        align-items: center;
        padding: 15px;
        border-radius: 10px;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .profile-image {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #FF5722;
        margin-right: 15px;
    }
    .profile-info {
        flex: 1;
    }
    .social-links {
        margin-top: 10px;
    }
    .social-links a {
        color: #007BFF;
        text-decoration: none;
        margin-right: 15px;
        font-weight: 500;
    }
    .social-links a:hover {
        text-decoration: underline;
    }
    .glossy-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .glossy-card:hover {
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        transform: translateY(-5px);
    }
    .nav-link {
        color: #333;
        text-decoration: none;
        padding: 10px 15px;
        border-radius: 5px;
        transition: all 0.2s;
    }
    .nav-link:hover {
        background-color: #f0f0f0;
    }
    .nav-link.active {
        background-color: #FF5722;
        color: white;
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
    try:
        lang = detect(text)
        if lang in INDIC_LANGUAGES:
            return lang
        return "en"  # Default to English if not an Indic language
    except LangDetectException:
        return "en"  # Default to English if detection fails

# Function to translate text using deep_translator
def translate_text(text, target_lang):
    if not text:
        return ""
    
    source_lang = detect_language(text)
    if source_lang == target_lang:
        return text
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

# Function to translate using GROQ API for more context-aware translations
def translate_with_groq(text, source_lang, target_lang, api_key):
    if not text or not api_key:
        return ""
    
    if source_lang == target_lang:
        return text
    
    try:
        client = groq.Client(api_key=api_key)
        source_lang_name = INDIC_LANGUAGES.get(source_lang, "Unknown")
        target_lang_name = INDIC_LANGUAGES.get(target_lang, "Unknown")
        
        prompt = f"""Translate the following text from {source_lang_name} to {target_lang_name}. 
        Maintain the cultural context, tone, and formatting of the original text.
        Ensure accuracy in grammar and script rendering.
        
        Text to translate: {text}"""
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional translator specializing in Indic languages."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            max_tokens=2048
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"GROQ API error: {str(e)}")
        # Fallback to deep_translator
        return translate_text(text, target_lang)

# Function to convert text to speech
def text_to_speech(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text to speech error: {str(e)}")
        return None

# Function to get audio player HTML
def get_audio_player(audio_path):
    audio_file = open(audio_path, 'rb')
    audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    return audio_html

# Developer Information Section
def show_developer_info():
    st.markdown('<div class="developer-profile">', unsafe_allow_html=True)
    
    try:
        profile_img = Image.open("nandesh25.jpg")
        st.image(profile_img, width=100, clamp=True)
    except:
        # If image is not found, use a placeholder
        st.markdown("👨‍💻")
    
    st.markdown("""
    <div class="profile-info">
        <h3>Nandesh Kalashetti</h3>
        <p>Creator of Bhasha Setu - Enterprise Indic Languages Translation Platform</p>
        <div class="social-links">
            <a href="https://nandesh-kalashettiportfilio2386.netlify.app/" target="_blank">Portfolio</a>
            <a href="https://github.com/Universe7Nandu" target="_blank">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🔤 भाषा सेतु")
    st.subheader("Bhasha Setu")
    
    lottie_translation = load_lottie_url("https://assets3.lottiefiles.com/private_files/lf30_P2uXE5.json")
    st_lottie(lottie_translation, height=200)
    
    # Navigation Menu
    menu = option_menu(
        menu_title=None,
        options=["Translate", "About", "API Settings", "Developer"],
        icons=["translate", "info-circle", "gear", "person"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#FF5722", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#FF5722"},
        }
    )
    
    if menu == "About":
        st.markdown("### About")
        st.info("""
        **भाषा सेतु (Bhasha Setu)** is a production-ready translation platform 
        specifically engineered for Indic languages. This enterprise solution 
        handles complex script variations while maintaining cultural context 
        across business communications.
        """)
        
        st.markdown("### Features")
        st.markdown("""
        - 🌐 Support for 15 Indic languages
        - 🔄 Real-time translation
        - 🗣️ Text-to-speech capability
        - 🖼️ Document translation
        - 💬 Bulk translation
        - 📱 Voice recognition (New!)
        - 🔄 Pronunciation helper (New!)
        - 📊 Custom analytics (New!)
        """)
    
    elif menu == "API Settings":
        st.markdown("### API Settings")
        
        # Show the loaded API key or allow user to input a custom one
        if GROQ_API_KEY:
            st.success("✅ GROQ API Key loaded successfully from environment variables!")
            use_default_key = st.checkbox("Use the loaded API key", value=True)
            
            if use_default_key:
                # Display a masked version of the key for verification
                masked_key = GROQ_API_KEY[:5] + "..." + GROQ_API_KEY[-5:]
                st.code(masked_key, language=None)
                groq_api_key = GROQ_API_KEY
            else:
                groq_api_key = st.text_input("Enter custom GROQ API Key", type="password")
        else:
            st.warning("⚠️ No API key found in environment variables. Please enter your GROQ API key below:")
            groq_api_key = st.text_input("GROQ API Key", type="password")
        
        st.markdown('<div class="custom-info-box">', unsafe_allow_html=True)
        st.markdown("""
        **Note**: For better translation quality and cultural context preservation, 
        please provide a GROQ API key. Without a key, the app will use the built-in 
        Google Translator which may have limitations with certain Indic languages.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            st.slider("Response Time (Delay in ms)", 0, 1000, 300, 50)
            st.checkbox("Enable Caching", value=True)
            tog.st_toggle_switch("Debug Mode", key="debug_mode", 
                                default_value=False, 
                                label_after=False)
            st.selectbox("Translation Mode", [
                "Standard (Faster)", 
                "Enhanced (Better quality)", 
                "Cultural Context (Best for Indic languages)"
            ])
    
    elif menu == "Developer":
        show_developer_info()
        
        st.markdown("### Technology Stack")
        st.markdown("""
        - Streamlit for UI
        - GROQ API for AI-powered translations
        - Google Translate as backup
        - gTTS for text-to-speech
        - Deployed on Streamlit Cloud
        """)
        
        st.markdown("### Project Goals")
        st.markdown("""
        This project aims to provide a high-quality translation service 
        specifically optimized for Indic languages, preserving cultural 
        context and nuances that are often lost in generic translation tools.
        """)

# Main content
if menu == "Translate":
    # Top section
    colored_header(
        label="Enterprise Indic Languages Translation Platform",
        description="Translate between Indic languages while preserving cultural context",
        color_name="red-70"
    )

    # Create tabs for different translation features
    tabs = st.tabs(["Text Translation", "Document Translation", "Bulk Translation", "Pronunciation Helper", "Analytics"])

    with tabs[0]:  # Text Translation Tab
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
            
            st.markdown('<div class="indic-text" id="translation-result" style="height: 250px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">', unsafe_allow_html=True)
            
            # Store translated text in session state
            if 'translated_text' not in st.session_state:
                st.session_state.translated_text = ""
                
            if source_text:
                with st.spinner("Translating..."):
                    # Try using GROQ API key in the following order:
                    # 1. Local variable from settings
                    # 2. Global variable from .env file
                    # 3. Fallback to Google Translate
                    api_key_to_use = None
                    
                    if 'groq_api_key' in locals() and groq_api_key:
                        api_key_to_use = groq_api_key
                    elif GROQ_API_KEY:
                        api_key_to_use = GROQ_API_KEY
                    
                    if api_key_to_use:
                        translated_text = translate_with_groq(
                            source_text, 
                            source_lang_code, 
                            target_lang_code,
                            api_key_to_use
                        )
                        translation_method = "GROQ API"
                    else:
                        translated_text = translate_text(source_text, target_lang_code)
                        translation_method = "Google Translate"
                    
                    st.session_state.translated_text = translated_text
                    st.markdown(f"<p>{translated_text}</p>", unsafe_allow_html=True)
                    
                    # Show which translation method was used
                    st.caption(f"Translated using: {translation_method}")
            else:
                if st.session_state.translated_text:
                    st.markdown(f"<p>{st.session_state.translated_text}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #888;'>Translation will appear here...</p>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            col2_1, col2_2, col2_3 = st.columns([1, 1, 1])
            with col2_1:
                copy_btn = st.button("📋 Copy", use_container_width=True)
                if copy_btn and st.session_state.translated_text:
                    st.toast("Copied to clipboard!")
            with col2_2:
                if source_text or st.session_state.translated_text:
                    speak_target_btn = st.button("🔊 Listen", key="speak_target", use_container_width=True)
                    
                    if speak_target_btn:
                        with st.spinner("Generating audio..."):
                            audio_path = text_to_speech(st.session_state.translated_text, target_lang_code)
                            
                            if audio_path:
                                st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
                                # Clean up the temporary file
                                os.remove(audio_path)
            with col2_3:
                share_btn = st.button("🔗 Share", use_container_width=True)
                if share_btn and st.session_state.translated_text:
                    st.toast("Translation link copied!")
        
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
                audio_path = text_to_speech(source_text, source_lang_code)
                if audio_path:
                    st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
                    # Clean up the temporary file
                    os.remove(audio_path)
        
        # New Feature: Voice Input
        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
        st.subheader("🎙️ Voice Input (New!)")
        st.markdown("Speak to translate - click the button and speak clearly")
        
        voice_col1, voice_col2 = st.columns([1, 3])
        with voice_col1:
            voice_btn = st.button("🎙️ Start Recording", use_container_width=True)
            if voice_btn:
                with st.spinner("Listening..."):
                    # Simulating voice recording and transcription
                    st.info("Voice input feature will connect to your microphone when deployed.")
                    st.session_state.source_text = "This is a simulated voice input. In production, this would use your actual speech."
                    st.rerun()
        with voice_col2:
            st.markdown("""
            1. Click the 'Start Recording' button
            2. Speak clearly in your chosen language
            3. Wait for transcription
            4. Review and translate
            """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

    with tabs[1]:  # Document Translation Tab
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.subheader("Document Translation")
        st.markdown("Upload documents to translate between Indic languages")
        
        # Document upload
        uploaded_file = st.file_uploader("Choose a text file", type=['txt', 'pdf', 'docx'])
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                doc_source_lang = st.selectbox(
                    "Select source language", 
                    options=list(INDIC_LANGUAGES.values()),
                    index=0,
                    key="doc_source_lang"
                )
                doc_source_lang_code = get_lang_code(doc_source_lang)
            
            with col2:
                doc_target_lang = st.selectbox(
                    "Select target language",
                    options=list(INDIC_LANGUAGES.values()),
                    index=4,  # Default to Marathi
                    key="doc_target_lang"
                )
                doc_target_lang_code = get_lang_code(doc_target_lang)
            
            # Quality settings
            quality_options = ["Standard (Faster)", "Enhanced (Better quality)", "Cultural Context (Best for Indic languages)"]
            selected_quality = st.select_slider("Translation Quality", options=quality_options, value=quality_options[1])
            
            translate_doc_btn = st.button("Translate Document", use_container_width=True)
            
            if translate_doc_btn:
                try:
                    with st.spinner("Processing document..."):
                        # Read content based on file type
                        if uploaded_file.name.endswith('.txt'):
                            file_content = uploaded_file.read().decode('utf-8')
                        elif uploaded_file.name.endswith('.pdf'):
                            st.info("PDF processing is simulated. In production, this would use a PDF extraction library.")
                            file_content = "Sample PDF content extracted for demonstration."
                        elif uploaded_file.name.endswith('.docx'):
                            st.info("DOCX processing is simulated. In production, this would use a DOCX extraction library.")
                            file_content = "Sample DOCX content extracted for demonstration."
                        else:
                            st.warning("Currently only supporting TXT files. PDF and DOCX will be added soon.")
                            file_content = "Unsupported file format"
                        
                        # Show content preview
                        with st.expander("Original Content Preview"):
                            st.text(file_content[:500] + "..." if len(file_content) > 500 else file_content)
                        
                        # Apply different quality settings
                        with st.status("Translation in progress...") as status:
                            status.update(label="Analyzing document structure...")
                            time.sleep(0.5)
                            
                            status.update(label="Processing language patterns...")
                            time.sleep(0.5)
                            
                            status.update(label="Translating content...")
                            # Try using GROQ API key in the following order:
                            # 1. Local variable from settings
                            # 2. Global variable from .env file
                            # 3. Fallback to Google Translate
                            api_key_to_use = None
                            
                            if 'groq_api_key' in locals() and groq_api_key:
                                api_key_to_use = groq_api_key
                            elif GROQ_API_KEY:
                                api_key_to_use = GROQ_API_KEY
                                
                            if api_key_to_use:
                                translated_content = translate_with_groq(
                                    file_content,
                                    doc_source_lang_code,
                                    doc_target_lang_code,
                                    api_key_to_use
                                )
                                translation_method = "GROQ API"
                            else:
                                # For larger documents, break into paragraphs for better translation
                                paragraphs = file_content.split('\n\n')
                                translated_paragraphs = []
                                
                                for i, para in enumerate(paragraphs):
                                    if para.strip():
                                        status.update(label=f"Translating paragraph {i+1}/{len(paragraphs)}...")
                                        translated_para = translate_text(para, doc_target_lang_code)
                                        translated_paragraphs.append(translated_para)
                                        time.sleep(0.2)  # Prevent rate limiting
                                
                                translated_content = '\n\n'.join(translated_paragraphs)
                                translation_method = "Google Translate"
                            
                            status.update(label="Finalizing translation...", state="complete")
                        
                        # Display translated content
                        with st.expander("Translated Content Preview", expanded=True):
                            st.markdown(f"<div class='indic-text'>{translated_content[:500] + '...' if len(translated_content) > 500 else translated_content}</div>", unsafe_allow_html=True)
                            st.caption(f"Translated using: {translation_method}")
                        
                        # Download options
                        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
                        st.subheader("Download Options")
                        
                        # Create download buttons for different formats
                        col1, col2, col3 = st.columns(3)
                        
                        # Text file download
                        translated_file = io.StringIO()
                        translated_file.write(translated_content)
                        file_name = uploaded_file.name.split('.')[0]
                        
                        with col1:
                            st.download_button(
                                label="Download as TXT",
                                data=translated_file.getvalue(),
                                file_name=f"{file_name}_translated.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            st.download_button(
                                label="Download as PDF",
                                data=translated_file.getvalue(),
                                file_name=f"{file_name}_translated.pdf",
                                mime="application/pdf",
                                help="Download the translated content as a PDF file"
                            )
                        
                        with col3:
                            st.download_button(
                                label="Download as DOCX",
                                data=translated_file.getvalue(),
                                file_name=f"{file_name}_translated.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                help="Download the translated content as a DOCX file"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
        
        # New Feature: Batch Document Translation
        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
        st.subheader("🔄 Batch Document Translation (New!)")
        st.markdown("Upload multiple documents to translate them all at once")
        
        st.file_uploader("Upload multiple documents", type=['txt', 'pdf', 'docx'], accept_multiple_files=True, key="batch_files")
        
        batch_col1, batch_col2 = st.columns(2)
        with batch_col1:
            batch_source = st.selectbox("Batch Source Language", options=list(INDIC_LANGUAGES.values()), index=14, key="batch_source")
        with batch_col2:
            batch_target = st.selectbox("Batch Target Language", options=list(INDIC_LANGUAGES.values()), index=0, key="batch_target")
        
        if st.button("Process Batch", use_container_width=True):
            st.info("Batch processing feature will be enabled in production. This would process multiple files at once.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

    with tabs[2]:  # Bulk Translation Tab
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.subheader("Bulk Translation")
        st.markdown("Translate multiple phrases at once")
        
        # Template download
        st.download_button(
            label="Download CSV Template",
            data="text,translation\nHello,\nGood morning,\nThank you,",
            file_name="translation_template.csv",
            mime="text/csv"
        )
        
        # Upload CSV
        uploaded_csv = st.file_uploader("Upload CSV with phrases to translate", type=['csv'])
        
        if uploaded_csv is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                bulk_source_lang = st.selectbox(
                    "Select source language", 
                    options=list(INDIC_LANGUAGES.values()),
                    index=14,  # Default to English
                    key="bulk_source_lang"
                )
                bulk_source_lang_code = get_lang_code(bulk_source_lang)
            
            with col2:
                bulk_target_lang = st.selectbox(
                    "Select target language",
                    options=list(INDIC_LANGUAGES.values()),
                    index=4,  # Default to Marathi
                    key="bulk_target_lang"
                )
                bulk_target_lang_code = get_lang_code(bulk_target_lang)
            
            st.checkbox("Include pronunciation guide", value=False, key="include_pronunciation")
            
            translate_bulk_btn = st.button("Translate All", use_container_width=True)
            
            if translate_bulk_btn:
                try:
                    with st.spinner("Translating phrases..."):
                        df = pd.read_csv(uploaded_csv)
                        
                        # Check if the dataframe has the correct format
                        if 'text' not in df.columns:
                            st.error("CSV must contain a 'text' column")
                        else:
                            # Create a translation column if it doesn't exist
                            if 'translation' not in df.columns:
                                df['translation'] = ''
                            
                            # Add pronunciation column if requested
                            if st.session_state.include_pronunciation and 'pronunciation' not in df.columns:
                                df['pronunciation'] = ''
                            
                            # Progress bar
                            progress_bar = st.progress(0)
                            
                            # Translate each phrase
                            for i, row in df.iterrows():
                                text = row['text']
                                if text and pd.notna(text):
                                    # Try using GROQ API key in the following order:
                                    # 1. Local variable from settings
                                    # 2. Global variable from .env file
                                    # 3. Fallback to Google Translate
                                    api_key_to_use = None
                                    
                                    if 'groq_api_key' in locals() and groq_api_key:
                                        api_key_to_use = groq_api_key
                                    elif GROQ_API_KEY:
                                        api_key_to_use = GROQ_API_KEY
                                        
                                    if api_key_to_use:
                                        translation = translate_with_groq(
                                            text, 
                                            bulk_source_lang_code,
                                            bulk_target_lang_code,
                                            api_key_to_use
                                        )
                                        translation_method = "GROQ API"
                                    else:
                                        translation = translate_text(text, bulk_target_lang_code)
                                        translation_method = "Google Translate"
                                    
                                    df.at[i, 'translation'] = translation
                                    
                                    # Add method column if it doesn't exist
                                    if 'method' not in df.columns:
                                        df['method'] = ''
                                    df.at[i, 'method'] = translation_method
                                    
                                    # Add pronunciation if requested
                                    if st.session_state.include_pronunciation:
                                        # This would use a proper pronunciation guide in production
                                        df.at[i, 'pronunciation'] = f"[Pronunciation for: {translation}]"
                                    
                                    # Update progress
                                    progress_bar.progress((i + 1) / len(df))
                                    time.sleep(0.1)  # To prevent rate limiting
                            
                            # Display the results
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # Download the results
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download Translated CSV",
                                data=csv,
                                file_name="translated_phrases.csv",
                                mime="text/csv"
                            )
                except Exception as e:
                    st.error(f"Error processing CSV: {str(e)}")
        
        # New feature: Excel compatibility
        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
        st.subheader("📊 Excel Compatibility (New!)")
        st.markdown("Upload Excel files for translation")
        
        excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'], key="excel_upload")
        
        if excel_file:
            st.info("Excel processing will be enabled in production. This would allow translating Excel spreadsheets while preserving formatting.")
            
            excel_cols = st.columns(2)
            with excel_cols[0]:
                st.selectbox("Excel Sheet", ["Sheet1", "Sheet2", "Sheet3"], key="excel_sheet")
            with excel_cols[1]:
                st.selectbox("Column to Translate", ["A", "B", "C", "D"], key="excel_column")
            
            if st.button("Process Excel", use_container_width=True):
                st.success("Excel translation would be processed here in production.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

    with tabs[3]:  # Pronunciation Helper Tab (New!)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.subheader("Pronunciation Helper")
        st.markdown("Learn how to properly pronounce words and phrases in Indic languages")
        
        pronunciation_col1, pronunciation_col2 = st.columns(2)
        
        with pronunciation_col1:
            pronunciation_lang = st.selectbox(
                "Select language",
                options=list(INDIC_LANGUAGES.values()),
                index=0,
                key="pronunciation_lang"
            )
            pronunciation_lang_code = get_lang_code(pronunciation_lang)
            
            pronunciation_text = st.text_input(
                "Enter word or phrase",
                placeholder="Type a word or phrase to learn pronunciation"
            )
            
            if st.button("Get Pronunciation", use_container_width=True) and pronunciation_text:
                with st.spinner("Generating pronunciation guide..."):
                    # In a production app, this would use a specialized pronunciation API
                    phonetic_spelling = f"Phonetic: [{pronunciation_text}]"
                    st.success(f"Pronunciation guide generated!")
                    
                    # Show phonetic spelling
                    st.markdown(f"### Phonetic Spelling")
                    st.markdown(f"<div class='indic-text'>{phonetic_spelling}</div>", unsafe_allow_html=True)
                    
                    # Generate and play audio
                    audio_path = text_to_speech(pronunciation_text, pronunciation_lang_code)
                    if audio_path:
                        st.markdown("### Audio Pronunciation")
                        st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
                        # Clean up the temporary file
                        os.remove(audio_path)
                    
                    # Show syllable breakdown
                    st.markdown("### Syllable Breakdown")
                    syllables = ' · '.join(pronunciation_text)
                    st.markdown(f"<div class='indic-text' style='font-size: 1.5rem;'>{syllables}</div>", unsafe_allow_html=True)
        
        with pronunciation_col2:
            st.markdown("### Common Phrases")
            
            # Common phrases by language
            common_phrases = {
                "hi": ["नमस्ते (Hello)", "धन्यवाद (Thank you)", "कृपया (Please)"],
                "mr": ["नमस्कार (Hello)", "धन्यवाद (Thank you)", "कृपया (Please)"],
                "bn": ["নমস্কার (Hello)", "ধন্যবাদ (Thank you)", "অনুগ্রহ করে (Please)"],
                "ta": ["வணக்கம் (Hello)", "நன்றி (Thank you)", "தயவுசெய்து (Please)"],
                "te": ["నమస్కారం (Hello)", "ధన్యవాదాలు (Thank you)", "దయచేసి (Please)"]
            }
            
            # Get current language code
            current_lang_code = pronunciation_lang_code
            
            # Display phrases for the selected language or default to Hindi
            phrases_to_show = common_phrases.get(current_lang_code, common_phrases["hi"])
            
            for phrase in phrases_to_show:
                with stylable_container(
                    key=f"phrase_{phrase}",
                    css_styles="""
                    {
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 5px 0;
                        background-color: #f9f9f9;
                        cursor: pointer;
                    }
                    :hover {
                        background-color: #f0f0f0;
                        border-color: #FF5722;
                    }
                    """
                ):
                    st.markdown(f"<div class='indic-text'>{phrase}</div>", unsafe_allow_html=True)
                    if st.button("🔊", key=f"play_{phrase}"):
                        clean_phrase = phrase.split(" (")[0]  # Extract just the native text
                        audio_path = text_to_speech(clean_phrase, current_lang_code)
                        if audio_path:
                            st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
                            # Clean up the temporary file
                            os.remove(audio_path)
            
            # Pronunciation tips
            st.markdown("### Pronunciation Tips")
            st.markdown("""
            - Listen carefully to the audio sample
            - Practice saying the word or phrase slowly
            - Break down difficult words into syllables
            - Pay attention to stress and intonation
            - Record yourself and compare with the sample
            """)
        
        # Pronunciation challenge section
        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
        st.subheader("🎯 Pronunciation Challenge (New!)")
        st.markdown("Test your pronunciation skills with these challenges")
        
        challenge_col1, challenge_col2, challenge_col3 = st.columns([2,1,2])
        
        with challenge_col1:
            st.markdown("### Today's Challenge")
            challenge_word = "नमस्कार" if current_lang_code == "mr" else "नमस्ते"
            st.markdown(f"<div class='indic-text' style='font-size: 2rem; text-align: center;'>{challenge_word}</div>", unsafe_allow_html=True)
            
            audio_path = text_to_speech(challenge_word, current_lang_code if current_lang_code in ["hi", "mr"] else "hi")
            if audio_path:
                st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
                # Clean up the temporary file
                os.remove(audio_path)
        
        with challenge_col2:
            st.markdown("### Score")
            st.markdown("<div style='font-size: 2rem; text-align: center;'>⭐⭐⭐</div>", unsafe_allow_html=True)
        
        with challenge_col3:
            st.markdown("### Your Turn")
            st.button("🎙️ Record Your Pronunciation", use_container_width=True)
            st.markdown("<div style='color: #888; text-align: center;'>Click to record your voice</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close glossy-card
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

    with tabs[4]:  # Analytics Tab (New!)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.subheader("Translation Analytics")
        st.markdown("Insights about your translation activities")
        
        # Mock data for analytics
        languages_used = {
            "Hindi": 42,
            "Marathi": 38,
            "English": 25,
            "Bengali": 15,
            "Tamil": 10,
            "Telugu": 8,
            "Others": 12
        }
        
        translation_history = [
            {"date": "2023-06-01", "count": 5},
            {"date": "2023-06-02", "count": 8},
            {"date": "2023-06-03", "count": 12},
            {"date": "2023-06-04", "count": 7},
            {"date": "2023-06-05", "count": 15},
            {"date": "2023-06-06", "count": 10},
            {"date": "2023-06-07", "count": 18}
        ]
        
        analytics_col1, analytics_col2 = st.columns(2)
        
        with analytics_col1:
            st.markdown("### Languages Used")
            
            # Create a dataframe for the chart
            langs = list(languages_used.keys())
            counts = list(languages_used.values())
            lang_df = pd.DataFrame({"Language": langs, "Count": counts})
            
            # Display bar chart
            st.bar_chart(lang_df.set_index("Language"))
            
            st.markdown("### Most Used Phrases")
            phrases_df = pd.DataFrame({
                "Phrase": ["Hello", "Thank you", "Good morning", "How are you?", "Goodbye"],
                "Count": [45, 32, 28, 24, 20]
            })
            st.dataframe(phrases_df, use_container_width=True, hide_index=True)
        
        with analytics_col2:
            st.markdown("### Translation History")
            
            # Create dataframe for the chart
            history_df = pd.DataFrame(translation_history)
            history_df["date"] = pd.to_datetime(history_df["date"])
            
            # Display line chart
            st.line_chart(history_df.set_index("date"))
            
            st.markdown("### Translation Efficiency")
            st.metric("Average Translation Time", "0.8 seconds", "-0.2s")
            
            efficiency_data = {
                "Metric": ["Characters Translated", "Documents Processed", "API Calls", "Cache Hits"],
                "Value": ["12,450", "8", "156", "42"]
            }
            st.dataframe(pd.DataFrame(efficiency_data), use_container_width=True, hide_index=True)
        
        # Export analytics section
        st.markdown('<div class="glossy-card">', unsafe_allow_html=True)
        st.subheader("📊 Export Analytics")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            st.download_button(
                label="Export as CSV",
                data=pd.DataFrame({
                    "Metric": ["Languages Used", "Phrases Translated", "Documents Processed", "Average Time"],
                    "Value": ["7", "150", "8", "0.8s"]
                }).to_csv(index=False),
                file_name="translation_analytics.csv",
                mime="text/csv"
            )
        
        with export_col2:
            st.download_button(
                label="Export as PDF",
                data="Analytics report would be generated as PDF",
                file_name="translation_analytics.pdf",
                mime="application/pdf"
            )
        
        with export_col3:
            if st.button("Share Report", use_container_width=True):
                st.success("Report link generated and copied to clipboard!")
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close glossy-card
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

# Display translation statistics
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Translation Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Languages Supported", "15", "+2")
with col2:
    st.metric("Translation Accuracy", "95%", "+3%")
with col3:
    st.metric("Response Time", "<1s", "-0.2s")
with col4:
    st.metric("Active Users", "850", "+125")

st.markdown('</div>', unsafe_allow_html=True)  # Close the card div

# Developer Information Section at the bottom
if menu != "Developer":
    show_developer_info()

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("© 2023 भाषा सेतु | Bhasha Setu - Enterprise Indic Languages Translation Platform")
st.markdown("Created by Nandesh Kalashetti | [Portfolio](https://nandesh-kalashettiportfilio2386.netlify.app/) | [GitHub](https://github.com/Universe7Nandu)")
st.markdown("</div>", unsafe_allow_html=True)
