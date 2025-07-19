import os
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
from docx import Document
from io import BytesIO

st.set_page_config(page_title="🎧 تفريغ الصوتية", layout="centered")

page_style = """
<style>
    .stApp {
        background-color: #eec9b0;
    }
    .main-header {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0;
        color: black;
    }
    .sub-header {
        font-size: 20px;
        text-align: center;
        margin-top: 0;
        margin-bottom: 30px;
        color: black;
        white-space: pre-line;
    }
    .custom-textarea textarea {
        background-color: white !important;
        color: black !important;
        font-size: 20px !important;
        height: 500px !important;
        direction: rtl !important;
        text-align: right !important;
        border-radius: 10px !important;
    }
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎧 تفريغ الصوتية</h1>', unsafe_allow_html=True)

new_text = """🥹✨إلـى شـيـخـتـي وأمـي الــحــبــيــبــة أقــدم لــكِ هــذه الــهديــة البــسيــطــة 🎁 بــمــنــاســبــة أنــكِ أصــبــحــتِ جــدة
🥹💝✨صــنــع بــحــب مــن طالـبـتـك الـمــجــتــهـدة بـدور"""
st.markdown(f'<p class="sub-header">{new_text}</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 ارفعي ملف صوتي أو فيديو", type=["mp3", "wav", "m4a", "ogg", "flac", "mp4", "mov", "avi", "mkv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    try:
        sound = AudioSegment.from_file(input_path)
        sound = sound.set_channels(1).set_frame_rate(16000)
        wav_path = input_path + "_converted.wav"
        sound.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        chunk_length = 20 * 1000  # 20 ثانية بدل 30
        total_length = len(sound)
        chunks = list(range(0, total_length, chunk_length))

        full_text = ""
        progress_text = st.empty()
        progress_bar = st.progress(0)

        for i, start in enumerate(chunks):
            end = min(start + chunk_length, total_length)
            chunk = sound[start:end]
            chunk_file = f"{wav_path}_chunk_{i}.wav"
            chunk.export(chunk_file, format="wav")

            with sr.AudioFile(chunk_file) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)  # زيادة مدة الضبط للضوضاء
                audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio, language="ar")
                full_text += text + "\n"
            except sr.UnknownValueError:
                full_text += "[لم يتم التعرف على هذا الجزء]\n"
            except sr.RequestError:
                full_text += "[خطأ في الاتصال بخدمة التعرف على الصوت]\n"

            os.remove(chunk_file)
            progress_text.text(f"🔄 جاري معالجة الجزء {i+1} من {len(chunks)}...")
            progress_bar.progress((i + 1) / len(chunks))

        st.success("✅ تم استخراج النص بنجاح!")

        with st.expander("📄 عرض النص المستخرج"):
            st.markdown('<div class="custom-textarea">', unsafe_allow_html=True)
            st.text_area("", value=full_text, height=500)
            st.markdown('</div>', unsafe_allow_html=True)

        doc = Document()
        for line in full_text.split('\n'):
            doc.add_paragraph(line)
        doc_stream = BytesIO()
        doc.save(doc_stream)
        doc_stream.seek(0)

        st.download_button(
            label="📥 تحميل النص بصيغة وورد (.docx)",
            data=doc_stream,
            file_name="transcription.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

        os.remove(input_path)
        os.remove(wav_path)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {e}")
