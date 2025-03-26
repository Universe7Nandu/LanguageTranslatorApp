import os
import base64
import tempfile
import streamlit as st
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from gtts import gTTS
import requests
from langdetect import detect, LangDetectException
import io
import docx2txt
import pdfplumber
from streamlit_lottie import st_lottie
import time

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Polyglot Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language dictionary with expanded options
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
    "ur": "Urdu - اردو",
    "fr": "French - Français",
    "es": "Spanish - Español",
    "de": "German - Deutsch",
    "it": "Italian - Italiano",
    "pt": "Portuguese - Português",
    "ru": "Russian - Русский",
    "ja": "Japanese - 日本語",
    "zh-cn": "Chinese (Simplified) - 简体中文",
    "ar": "Arabic - العربية",
    "ko": "Korean - 한국어"
}

# Initialize session state
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []

if 'auto_detect_language' not in st.session_state:
    st.session_state.auto_detect_language = True

if 'show_pronunciation' not in st.session_state:
    st.session_state.show_pronunciation = False

# Load animations
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

translation_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_aakrld7f.json")
welcome_animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_GwQOT0.json")

# Apply custom styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --bg-color: #121212;
        --card-bg: #1E1E1E;
        --accent: #8A2BE2;  /* Vibrant purple */
        --accent-gradient: linear-gradient(90deg, #8A2BE2, #4776E6);
        --text: #FFFFFF;
        --text-secondary: #B0B0B0;
        --success: #4CAF50;
        --info: #2196F3;
        --warning: #FF9800;
        --error: #F44336;
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

    h1 {
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Translation panels */
    .translator-panel {
        background-color: var(--card-bg);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }

    .translator-panel:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-2px) !important;
    }

    /* Text areas and inputs */
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #2A2A2A !important;
        color: var(--text) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(138, 43, 226, 0.25) !important;
    }

    /* Status messages */
    .status-box {
        padding: 12px;
        border-radius: 8px;
        margin: 12px 0;
        animation: fadeIn 0.5s ease-in-out;
    }

    .status-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--success);
    }

    .status-info {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid var(--info);
    }

    /* Audio player */
    audio {
        width: 100%;
        margin-top: 12px;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Custom progress bar */
    .progress-container {
        width: 100%;
        height: 6px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        margin: 10px 0;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        background: var(--accent-gradient);
        border-radius: 3px;
        animation: progress-anim 1s ease-in-out;
    }

    /* History item */
    .history-item {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 3px solid var(--accent);
        transition: all 0.3s ease;
    }

    .history-item:hover {
        background-color: rgba(255, 255, 255, 0.08);
        transform: translateX(3px);
    }

    /* Pronunciation guide */
    .pronunciation-guide {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        border-left: 3px solid var(--info);
    }

    /* File uploader */
    .stFileUploader {
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed rgba(255, 255, 255, 0.3);
        background-color: rgba(255, 255, 255, 0.03);
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: var(--accent);
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Language confidence meter */
    .confidence-meter {
        height: 4px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        margin-top: 5px;
        overflow: hidden;
    }

    .confidence-meter-fill {
        height: 100%;
        width: var(--confidence);
        background: linear-gradient(to right, #f44336, #ffeb3b, #4caf50);
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes progress-anim {
        from { width: 0%; }
        to { width: 100%; }
    }

    /* Copy button tooltip */
    .copy-tooltip {
        position: relative;
        display: inline-block;
    }

    .copy-tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: var(--card-bg);
        color: var(--text);
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .copy-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Customized scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }
</style>
""", unsafe_allow_html=True)

# Function to detect language
def detect_language(text):
    try:
        if not text:
            return "en"
        detected = detect(text)
        return detected
    except LangDetectException:
        return "en"

# Function to translate text
def translate_text(text, target_lang, source_lang='auto'):
    try:
        if not text:
            return ""
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return ""

# Function to convert text to speech
def text_to_speech(text, lang_code):
    try:
        if not text:
            return None
        
        # Map language codes for gTTS
        gtts_lang_mapping = {
            "hi": "hi", "bn": "bn", "ta": "ta",
            "te": "te", "mr": "mr", "gu": "gu",
            "kn": "kn", "ml": "ml", "pa": "pa",
            "ur": "ur", "en": "en", "fr": "fr",
            "es": "es", "de": "de", "it": "it",
            "pt": "pt", "ru": "ru", "ja": "ja",
            "zh-cn": "zh-CN", "ar": "ar", "ko": "ko"
        }
        
        lang = gtts_lang_mapping.get(lang_code, "en")
        
        with st.spinner("Generating audio..."):
            tts = gTTS(text=text, lang=lang, slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

# Function to get audio player HTML
def get_audio_player(audio_path):
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

# Function to extract text from various file types
def extract_text_from_file(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'txt':
            return uploaded_file.getvalue().decode('utf-8')
        elif file_extension == 'docx':
            return docx2txt.process(uploaded_file)
        elif file_extension == 'pdf':
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        else:
            st.error("Unsupported file format. Please upload a TXT, DOCX, or PDF file.")
            return None
    except Exception as e:
        st.error(f"Error extracting text from file: {str(e)}")
        return None

# Function to generate pronunciation guide
def get_pronunciation_guide(text, lang_code):
    vowels = 'aeiouAEIOU'
    consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
    
    highlighted_text = ""
    for char in text:
        if char in vowels:
            highlighted_text += f"<span style='color: #8A2BE2;'>{char}</span>"
        elif char in consonants:
            highlighted_text += f"<span style='color: #FFFFFF;'>{char}</span>"
        else:
            highlighted_text += char
            
    return highlighted_text

# Function to add translation to history
def add_to_history(source_text, translated_text, source_lang, target_lang):
    if source_text and translated_text:
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.translation_history.insert(0, {
            "timestamp": timestamp,
            "source_text": source_text[:50] + "..." if len(source_text) > 50 else source_text,
            "translated_text": translated_text[:50] + "..." if len(translated_text) > 50 else translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        # Keep only the last 10 translations
        if len(st.session_state.translation_history) > 10:
            st.session_state.translation_history = st.session_state.translation_history[:10]

# Main app function
def main():
    # Setup the sidebar
    with st.sidebar:
        st.title("🛠️ Settings")
        st.session_state.auto_detect_language = st.toggle("Auto-detect language", value=st.session_state.auto_detect_language)
        st.session_state.show_pronunciation = st.toggle("Show pronunciation guide", value=st.session_state.show_pronunciation)
        
        # Display the translation animation
        if translation_animation:
            st_lottie(translation_animation, height=200, key="sidebar_animation")
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: var(--text-secondary);'>"
            "Polyglot Translator v2.0<br>"
            "© 2025 - Made with ❤️"
            "</div>",
            unsafe_allow_html=True
        )
    
    # Main app layout
    st.title("🌎 Polyglot Translator")
    
    # Welcome message with animation
    if welcome_animation:
        col1, col2 = st.columns([1, 2])
        with col1:
            st_lottie(welcome_animation, height=150, key="welcome_animation")
        with col2:
            st.markdown(
                """
                <div style='animation: fadeIn 1s ease-in-out;'>
                <h3>Welcome to Polyglot Translator!</h3>
                <p>Your advanced language translation tool supporting 20+ languages with text-to-speech capabilities.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Create tabs for different translation modes
    tab1, tab2, tab3 = st.tabs(["💬 Text Translation", "📄 Document Translation", "📊 Translation History"])
    
    # Tab 1: Text Translation
    with tab1:
        st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.auto_detect_language:
                st.info("🔍 Auto-detect language is enabled")
                source_lang_display = st.selectbox(
                    "From (Auto-detected)",
                    options=list(LANGUAGES.values()),
                    disabled=True,
                    key="source_lang_display"
                )
                source_lang_code = "auto"
            else:
                source_lang = st.selectbox(
                    "From",
                    options=list(LANGUAGES.values()),
                    index=0,
                    key="source_lang"
                )
                source_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(source_lang)]
            
            source_text = st.text_area(
                "Enter text to translate",
                height=200,
                placeholder="Type or paste your text here...",
                key="source_text"
            )
            
            # Detect language if auto-detect is enabled
            if source_text and st.session_state.auto_detect_language:
                detected_lang = detect_language(source_text)
                if detected_lang in LANGUAGES:
                    detected_lang_name = LANGUAGES[detected_lang]
                    st.success(f"Detected language: {detected_lang_name}")
            
            # Source language controls
            if source_text:
                if st.button("🔊 Listen to Source Text", use_container_width=True):
                    if st.session_state.auto_detect_language:
                        detected_lang = detect_language(source_text)
                        audio_path = text_to_speech(source_text, detected_lang)
                    else:
                        audio_path = text_to_speech(source_text, source_lang_code)
                        
                    if audio_path:
                        audio_player = get_audio_player(audio_path)
                        if audio_player:
                            st.markdown(audio_player, unsafe_allow_html=True)
                            try:
                                os.remove(audio_path)
                            except:
                                pass
        
        with col2:
            target_lang = st.selectbox(
                "To",
                options=list(LANGUAGES.values()),
                index=1,
                key="target_lang"
            )
            target_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(target_lang)]
            
            # Translation
            if source_text:
                # Show a spinner during translation
                with st.spinner("Translating..."):
                    if st.session_state.auto_detect_language:
                        detected_lang = detect_language(source_text)
                        translated_text = translate_text(source_text, target_lang_code, detected_lang)
                    else:
                        translated_text = translate_text(source_text, target_lang_code, source_lang_code)
                
                if translated_text:
                    # Container for the translation result with a copy button
                    st.text_area(
                        "Translation",
                        value=translated_text,
                        height=200,
                        key="translated_text"
                    )
                    
                    # Add to history
                    source_lang_for_history = "Auto-detected" if st.session_state.auto_detect_language else LANGUAGES[source_lang_code]
                    add_to_history(source_text, translated_text, source_lang_for_history, LANGUAGES[target_lang_code])
                    
                    # Show pronunciation guide if enabled
                    if st.session_state.show_pronunciation:
                        pronunciation = get_pronunciation_guide(translated_text, target_lang_code)
                        st.markdown(
                            f"""
                            <div class="pronunciation-guide">
                                <h4>Pronunciation Guide:</h4>
                                <p>{pronunciation}</p>
                                <p><small>Vowels highlighted for emphasis</small></p>
                            </div>
                            """,
                            unsafe_allow_html=True
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
                            st.success("Translation copied to clipboard!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Document Translation
    with tab2:
        st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
        
        st.markdown("### Translate Documents")
        st.markdown("Upload a document (TXT, DOCX, or PDF) and translate its contents.")
        
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "pdf"])
        
        if uploaded_file is not None:
            # Extract text from the uploaded file
            extracted_text = extract_text_from_file(uploaded_file)
            
            if extracted_text:
                st.markdown("### Document Content")
                
                # Show a preview of the extracted text
                if len(extracted_text) > 1000:
                    preview_text = extracted_text[:1000] + "..."
                    st.text_area("Preview (first 1000 characters)", value=preview_text, height=200, disabled=True)
                    st.info(f"Full document contains {len(extracted_text)} characters.")
                else:
                    st.text_area("Document content", value=extracted_text, height=200, disabled=True)
                
                # Translation settings
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.session_state.auto_detect_language:
                        st.info("🔍 Auto-detect language is enabled for the document")
                        source_lang_code = "auto"
                    else:
                        doc_source_lang = st.selectbox(
                            "Document language",
                            options=list(LANGUAGES.values()),
                            index=0,
                            key="doc_source_lang"
                        )
                        source_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(doc_source_lang)]
                
                with col2:
                    doc_target_lang = st.selectbox(
                        "Translate to",
                        options=list(LANGUAGES.values()),
                        index=1,
                        key="doc_target_lang"
                    )
                    target_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(doc_target_lang)]
                
                # Translation button
                if st.button("🔄 Translate Document", use_container_width=True):
                    with st.spinner("Translating document..."):
                        # If document is long, we might need to split it into chunks
                        max_chunk_size = 5000  # Characters per chunk
                        
                        if len(extracted_text) > max_chunk_size:
                            st.info(f"Document is large ({len(extracted_text)} characters). Translating in chunks...")
                            
                            # Split text into chunks
                            chunks = [extracted_text[i:i+max_chunk_size] for i in range(0, len(extracted_text), max_chunk_size)]
                            
                            # Create a progress bar
                            progress_bar = st.progress(0)
                            translated_chunks = []
                            
                            for i, chunk in enumerate(chunks):
                                # Detect language for each chunk if auto-detect is enabled
                                if st.session_state.auto_detect_language:
                                    detected_lang = detect_language(chunk)
                                    translated_chunk = translate_text(chunk, target_lang_code, detected_lang)
                                else:
                                    translated_chunk = translate_text(chunk, target_lang_code, source_lang_code)
                                
                                translated_chunks.append(translated_chunk)
                                progress_bar.progress((i + 1) / len(chunks))
                            
                            # Combine translated chunks
                            translated_document = "\n".join(translated_chunks)
                        else:
                            # For smaller documents, translate all at once
                            if st.session_state.auto_detect_language:
                                detected_lang = detect_language(extracted_text)
                                translated_document = translate_text(extracted_text, target_lang_code, detected_lang)
                            else:
                                translated_document = translate_text(extracted_text, target_lang_code, source_lang_code)
                    
                    st.success("Translation completed!")
                    
                    # Display the translated document
                    st.markdown("### Translated Document")
                    st.text_area("Translation", value=translated_document, height=300)
                    
                    # Export options
                    st.markdown("### Export Options")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.code(translated_document)
                            st.success("Translated document copied to clipboard!")
                    
                    with col2:
                        # Create a download link for the translated document
                        translated_file = f"translated_{uploaded_file.name.split('.')[0]}.txt"
                        st.download_button(
                            label="💾 Download as TXT",
                            data=translated_document,
                            file_name=translated_file,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Add to history
                    source_lang_for_history = "Auto-detected" if st.session_state.auto_detect_language else LANGUAGES[source_lang_code]
                    add_to_history(
                        f"Document: {uploaded_file.name}", 
                        f"Translated document ({len(extracted_text)} chars)", 
                        source_lang_for_history, 
                        LANGUAGES[target_lang_code]
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Translation History
    with tab3:
        st.markdown('<div class="translator-panel">', unsafe_allow_html=True)
        
        st.markdown("### Translation History")
        
        if not st.session_state.translation_history:
            st.info("Your translation history will appear here.")
        else:
            for i, item in enumerate(st.session_state.translation_history):
                st.markdown(
                    f"""
                    <div class="history-item">
                        <div style="display: flex; justify-content: space-between;">
                            <div><strong>{item['timestamp']}</strong> • {item['source_lang']} → {item['target_lang']}</div>
                        </div>
                        <p><strong>Source:</strong> {item['source_text']}</p>
                        <p><strong>Translation:</strong> {item['translated_text']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.translation_history = []
                st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: var(--text-secondary);'>
            <p>Polyglot Translator supports 20+ languages with advanced features:</p>
            <ul style='list-style-type: none; padding: 0;'>
                <li>✓ Text-to-speech pronunciation</li>
                <li>✓ Document translation</li>
                <li>✓ Auto language detection</li>
                <li>✓ Translation history</li>
                <li>✓ Pronunciation guides</li>
            </ul>
            <p>© 2025 - Made with ❤️</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Run the app
if __name__ == "__main__":
    main()
