import streamlit as st
import cv2
import numpy as np
from moviepy.editor import ImageSequenceClip
import base64
from llm_inference import LLMInference
import time

def hypothetical_function(image):
    # Assume this function modifies the image in some way
    # For demonstration, let's just invert the colors of the image
    return cv2.bitwise_not(image)

def generate_video_from_images(images, fps=24):
    clip = ImageSequenceClip(images, fps=fps)
    video_path = "output_video.mp4"
    clip.write_videofile(video_path, codec='libx264')
    return video_path

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode()

def base64_to_image(base64_str):
    decoded = base64.b64decode(base64_str)
    np_data = np.fromstring(decoded, np.uint8)
    return cv2.imdecode(np_data, cv2.IMREAD_COLOR)

st.title("Image to Video Generator")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    initial_image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    st.image(initial_image, caption="Uploaded Image", use_column_width=True)

    frames = []
    current_image = initial_image

    total_frames = 1 * 2  # 12 fps * 2 seconds = 720 frames
    batch_size = 1
    batches = total_frames // batch_size

    for batch in range(batches):
        for _ in range(batch_size):
            current_image = LLMInference().run_image_inference_openai(current_image)
            frames.append(current_image)
        time.sleep(60)  # Wait for 60 seconds before processing the next batch

    # Generate the video
    video_path = generate_video_from_images(frames)

    # Provide the video for download
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()

    st.video(video_path)

    st.download_button(
        label="Download video",
        data=video_bytes,
        file_name="output_video.mp4",
        mime="video/mp4"
    )
