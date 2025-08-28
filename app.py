import streamlit as st
import random
import json
import os
import random as rand
from streamlit_mic_recorder import mic_recorder
from ai import AIProcessor

# Paths and folders
PROVERBS_PATH = "proverbs.json"
USER_AUDIO_INDEX = "user_audio_index.json"
USER_AUDIO_FOLDER = "user_audios"

# Make sure folder exists
os.makedirs(USER_AUDIO_FOLDER, exist_ok=True)

@st.cache_data
def load_proverbs():
    with open(PROVERBS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # Add IDs to proverbs
    for idx, proverb in enumerate(data):
        proverb["id"] = idx + 1
    return data

def save_audio_index(entry):
    if os.path.exists(USER_AUDIO_INDEX):
        with open(USER_AUDIO_INDEX, encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(entry)
    with open(USER_AUDIO_INDEX, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

# Load proverbs + AI
proverbs = load_proverbs()
ai = AIProcessor()

# Streamlit UI
st.title("🎙️ Palukulu: Practice Telugu Proverbs")

if "current_proverb" not in st.session_state:
    st.session_state.current_proverb = random.choice(proverbs)
proverb = st.session_state.current_proverb

st.subheader(f"Proverb ID: {proverb['id']}")
st.markdown(f"**{proverb['Original']}**")
if proverb.get("English"):
    st.markdown(f"*English:* {proverb['English']}")

st.markdown("### Speak this proverb:")

# Mic recorder (direct WAV)
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop Recording",
    key="mic_recorder",
    format="wav"
)

if audio_data is not None:
    audio_bytes = audio_data["bytes"]

    file_name = f"user_audio_{proverb['id']}_{rand.randint(1000, 9999)}.wav"
    file_path = os.path.join(USER_AUDIO_FOLDER, file_name)

    # Save WAV directly
    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    st.audio(file_path)

    # Transcribe
    transcription = ai.speech_to_text(file_path)
    st.info(f"📝 Transcription: {transcription}")

    # Similarity score
    similarity = ai.compare_texts(proverb["Original"], transcription)
    st.write(f"🔍 Similarity score: **{similarity:.2f}**")

    # Save index
    entry = {
        "proverb_id": proverb["id"],
        "proverb_text": proverb["Original"],
        "audio_path": file_path,
        "transcription": transcription,
        "similarity_score": similarity,
    }
    save_audio_index(entry)

# Next button
if st.button("➡️ Next Proverb"):
    st.session_state.current_proverb = random.choice(proverbs)
    st.rerun()
