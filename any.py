import os
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
import tempfile

st.title("🎧 تفريغ صوتي من أي ملف صوتي أو فيديو")

uploaded_file = st.file_uploader("📤 ارفع ملف صوتي أو فيديو", type=["mp3","wav","m4a","ogg","flac","mp4","mov","avi","mkv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    try:
        # تحويل الملف إلى wav بمواصفات للتعرف على الصوت
        sound = AudioSegment.from_file(input_path)
        sound = sound.set_channels(1).set_frame_rate(16000)
        wav_path = input_path + "_converted.wav"
        sound.export(wav_path, format="wav")
        
        recognizer = sr.Recognizer()
        chunk_length = 30 * 1000  # 30 ثانية
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
            progress_bar.progress((i+1)/len(chunks))

        st.success("✅ تم استخراج النص بنجاح!")
        st.text_area("📄 النص المستخرج:", value=full_text, height=400)
        st.download_button("📥 تحميل النص", data=full_text, file_name="transcription.txt")
        
        os.remove(input_path)
        os.remove(wav_path)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {e}")