import streamlit as st
import openai
import tempfile
from pathlib import Path
import os
from dotenv import load_dotenv
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import wave
import datetime

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def setup_stt():
    """
    Set up the speech-to-text functionality with a microphone button
    Returns the transcribed text when audio is recorded
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Initialize session states
    if "recording" not in st.session_state:
        st.session_state.recording = False
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = []

    def audio_callback(frame):
        """Callback to handle audio frames"""
        if st.session_state.recording:
            st.session_state.audio_data.append(frame.to_ndarray())
        return frame

    # Hide WebRTC default elements
    st.markdown("""
        <style>
        .stButton button {
            background-color: transparent;
            border: none;
            outline: none;
            box-shadow: none;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            gap: 0rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create a single column for the microphone
    col1, col2 = st.columns([1, 20])
    
    with col1:
        # Initialize WebRTC
        webrtc_ctx = webrtc_streamer(
            key="audio-recorder",
            mode=WebRtcMode.SENDONLY,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"audio": True, "video": False},
            audio_frame_callback=audio_callback,
            async_processing=True
        )

        # Handle recording button
        if st.button("🎤", key="mic_button"):
            st.session_state.recording = not st.session_state.recording
            if not st.session_state.recording and len(st.session_state.audio_data) > 0:
                try:
                    # Convert audio data to wav format
                    audio_array = np.concatenate(st.session_state.audio_data)
                    audio_frame = av.AudioFrame.from_ndarray(
                        audio_array,
                        format='s16',
                        layout='mono'
                    )
                    audio_bytes = audio_frame.to_ndarray().tobytes()
                    
                    # Save as WAV file
                    temp_audio_path = temp_dir / "temp_audio.wav"
                    with wave.open(str(temp_audio_path), 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(48000)
                        wav_file.writeframes(audio_bytes)
                    
                    # Transcribe using Whisper API
                    with open(temp_audio_path, "rb") as audio_file:
                        transcript = openai.Audio.transcribe(
                            "whisper-1",
                            audio_file
                        )
                    
                    # Clean up
                    os.remove(temp_audio_path)
                    st.session_state.audio_data = []
                    
                    return transcript.text
                    
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
                    st.session_state.audio_data = []
                    return None

    # Show recording status
    with col2:
        if st.session_state.recording:
            st.markdown("🔴 Recording... Click microphone again to stop")
    
    return None 