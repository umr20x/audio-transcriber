import os
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
import tempfile

# إعداد صفحة Streamlit
st.set_page_config(page_title="🎧 تفريغ الصوتية", layout="centered")

# إضافة CSS لتغيير لون خلفية الصفحة ولون الخط
page_bg = """
<style>
    .stApp {
        background-color: #eec9b0;
        color: black;  /* لون الخط الأسود عام */
    }
    .main-header {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0;
        color: black;  /* لون الخط الأسود */
    }
    .sub-header {
        font-size: 20px;
        text-align: center;
        margin-top: 0;
        margin-bottom: 30px;
        color: black;  /* لون الخط الأسود */
    }
    textarea {
        color: black !important;  /* نص مربع النص */
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# العنوان والنص تحته (بدون كلمة "مع سماعات")
st.markdown('<h1 class="main-header">🎧 تفريغ الصوتية</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header"> 🥹✨إلـى شـيـخـتـي وأمـي الــحــبــيــبــة أقــدم لــكِ هــذه الــهديــة البــسيــطــة 🎁 بــمــنــاســبــة أنــكِ أصــبــحــتِ جــدة<br> 🥹💝✨صــنــع بــحــب مــن طالـبـتـك الـمــجــتــهـدة بـدور </p>',
    unsafe_allow_html=True)

# رفع الملف
uploaded_file = st.file_uploader("📤 ارفع ملف صوتي أو فيديو", type=["mp3", "wav", "m4a", "ogg", "flac", "mp4", "mov", "avi", "mkv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    try:
        with st.spinner("⏳ جاري معالجة وتحويل الصوت، يرجى الانتظار..."):
            sound = AudioSegment.from_file(input_path)
            sound = sound.set_channels(1).set_frame_rate(16000)
            wav_path = input_path + "_converted.wav"
            sound.export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            chunk_length = 30 * 1000
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
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.record(source)

                try:
                    text = recognizer.recognize_google(audio, language="ar")
                    full_text += text + "\n"
                except sr.UnknownValueError:
                    full_text += "[لم يتم التعرف على هذا الجزء]\n"
                except sr.RequestError:
                    full_text += "[خطأ في الاتصال بخدمة التعرف على الصوت]\n"

                os.remove(chunk_file)
                progress_text.text(f"🔹 معالجة الجزء {i+1} من {len(chunks)}")
                progress_bar.progress((i + 1) / len(chunks))

        st.success("✅ تم استخراج النص بنجاح!")
        with st.expander("📄 عرض النص المستخرج"):
            st.text_area("", value=full_text, height=400)

        st.download_button("📥 تحميل النص", data=full_text, file_name="transcription.txt", use_container_width=True)

        os.remove(input_path)
        os.remove(wav_path)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {e}")
