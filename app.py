import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time

# 🌌 Supernova static wallpaper
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://cdn.pixabay.com/photo/2013/07/18/10/56/supernova-163711_1280.jpg");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ✨ Animated GIF element (motion effect at top)
st.image("https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif", use_column_width=True)

# 🎨 Custom Title
st.markdown(
    "<h1 style='text-align: center; color: darkblue; font-family: Verdana; font-size: 50px;'>"
    "READIFY AI...BY SIDDHARTH JAIN</h1>",
    unsafe_allow_html=True
)

# Load secrets from Streamlit Cloud
speech_key = st.secrets["speech_key"]
speech_region = st.secrets["speech_region"]
vision_key = st.secrets["vision_key"]
vision_endpoint = st.secrets["vision_endpoint"]

# Azure clients
computervision_client = ComputerVisionClient(
    vision_endpoint,
    CognitiveServicesCredentials(vision_key)
)

def extract_text(image_path):
    with open(image_path, "rb") as image_stream:
        ocr_result = computervision_client.read_in_stream(image_stream, raw=True)
    operation_location = ocr_result.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]
    while True:
        result = computervision_client.get_read_result(operation_id)
        if result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)
    text_output = ""
    if result.status == OperationStatusCodes.succeeded:
        for page_result in result.analyze_result.read_results:
            for line in page_result.lines:
                text_output += line.text + "\n"
    return text_output

def text_to_speech_file(text, filename="output.wav"):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    synthesizer.speak_text_async(text).get()
    return filename

# Streamlit UI
task = st.radio("Choose a task:", ["Image → Text", "Text → Speech", "Image → Speech"])

uploaded_file = st.file_uploader("Upload a PNG image", type=["png"])

if task == "Image → Text" and uploaded_file:
    with open("temp.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    extracted_text = extract_text("temp.png")
    st.subheader("Extracted Text:")
    st.write(extracted_text)

elif task == "Text → Speech":
    text_input = st.text_area("Enter text to speak:")
    if st.button("Speak"):
        audio_file = text_to_speech_file(text_input, "tts.wav")
        st.audio(audio_file)

elif task == "Image → Speech" and uploaded_file:
    with open("temp.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    extracted_text = extract_text("temp.png")
    st.subheader("Extracted Text:")
    st.write(extracted_text)
    if st.button("Speak Extracted Text"):
        audio_file = text_to_speech_file(extracted_text, "image_speech.wav")
        st.audio(audio_file)
