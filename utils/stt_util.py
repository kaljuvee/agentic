import streamlit as st
import openai
import tempfile
from pathlib import Path
import os
from dotenv import load_dotenv

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
    
    # Verify API key is available
    if not openai.api_key:
        st.error("OpenAI API key not found in environment variables")
        return None
    
    # Create a button with microphone icon
    if "recording" not in st.session_state:
        st.session_state.recording = False
    
    col1, col2 = st.columns([1, 20])
    with col1:
        if st.button("🎤", key="mic_button"):
            st.session_state.recording = True
            
            # Record audio using streamlit-webrtc
            audio_file = st_audiorec()
            
            if audio_file is not None:
                # Save the audio file temporarily
                temp_audio_path = temp_dir / "temp_audio.wav"
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file)
                
                try:
                    # Transcribe using Whisper API
                    with open(temp_audio_path, "rb") as audio_file:
                        transcript = openai.Audio.transcribe(
                            "whisper-1",
                            audio_file
                        )
                    
                    # Clean up temporary file
                    os.remove(temp_audio_path)
                    
                    # Return transcribed text
                    return transcript.text
                    
                except Exception as e:
                    st.error(f"Error transcribing audio: {str(e)}")
                    return None
                
            st.session_state.recording = False
    
    # Show recording status
    with col2:
        if st.session_state.recording:
            st.write("🔴 Recording...")
    
    return None

def st_audiorec():
    """
    Custom component for audio recording
    Returns the audio data as bytes
    """
    # Import here to avoid dependency issues
    from streamlit_webrtc import webrtc_streamer
    import av
    import numpy as np
    
    audio_data = []
    
    def audio_callback(frame):
        """Callback to handle audio frames"""
        audio_data.append(frame.to_ndarray())
        return frame
    
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=webrtc_streamer.AUDIO_ONLY,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"audio": True},
        audio_frame_callback=audio_callback,
    )
    
    if not webrtc_ctx.state.playing and len(audio_data) > 0:
        # Convert audio data to wav format
        audio_array = np.concatenate(audio_data)
        audio_frame = av.AudioFrame.from_ndarray(
            audio_array,
            format='s16',
            layout='mono'
        )
        audio_bytes = audio_frame.to_ndarray().tobytes()
        return audio_bytes
    
    return None 