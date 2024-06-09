import streamlit as st
import os
import shutil
import time
import json
import uuid
from datetime import datetime, timedelta
from llm_inference import LLMInference
from config import read_openai_config
from streamlit.components.v1 import html

openai_config = read_openai_config()

# Load access codes
def load_access_codes():
    with open("access_codes.json", "r") as file:
        return json.load(file)

access_codes = load_access_codes()

# Load sessions
def load_sessions():
    with open("sessions.json", "r") as file:
        return json.load(file)

# Save sessions
def save_sessions(sessions):
    with open("sessions.json", "w") as file:
        json.dump(sessions, file)

# Create a session
def create_session(email):
    sessions = load_sessions()
    session_id = uuid.uuid4().hex
    sessions[email] = {"session_id": session_id, "timestamp": datetime.now().isoformat()}
    save_sessions(sessions)
    return session_id

# Validate a session
def validate_session(email, session_id):
    sessions = load_sessions()
    if email in sessions:
        session = sessions[email]
        if session["session_id"] == session_id:
            session_time = datetime.fromisoformat(session["timestamp"])
            if datetime.now() - session_time < timedelta(minutes=30):
                return True
    return False

# Terminate a session
def terminate_session(email):
    sessions = load_sessions()
    if email in sessions:
        del sessions[email]
        save_sessions(sessions)

# Authentication
def authenticate(email, code):
    return access_codes.get(email) == code

# Function to clean up generated files
def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# Endpoint to handle cleanup requests
def handle_cleanup_request():
    if "output" in st.session_state and st.session_state["output"]:
        cleanup_files([st.session_state["output"]["png_path"], st.session_state["output"]["drawio_path"]])
        st.session_state["submitted"] = False
        st.session_state["output"] = None
        st.session_state["input_data"] = None

# App state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "email" not in st.session_state:
    st.session_state["email"] = None
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "output" not in st.session_state:
    st.session_state["output"] = None
if "last_interaction" not in st.session_state:
    st.session_state["last_interaction"] = time.time()
if "input_data" not in st.session_state:
    st.session_state["input_data"] = None

# Function to check idle time and cleanup
def check_idle_time():
    if time.time() - st.session_state["last_interaction"] > 30:  # 30 seconds
        handle_cleanup_request()
        terminate_session(st.session_state["email"])
        st.session_state["authenticated"] = False
        st.stop()

# Update last interaction time
def update_interaction():
    st.session_state["last_interaction"] = time.time()

# Inject JavaScript to handle page unload
html("""
<script>
window.addEventListener('beforeunload', function (event) {
    // Send a request to the cleanup endpoint
    fetch('/clean-up', { method: 'POST' });
});
</script>
""")

# Authentication Form
if not st.session_state["authenticated"]:
    st.title("Welcome to misty.ai")
    st.markdown("Please provide the access code mailed to your registered Email address")
    email = st.text_input("Email Address")
    code = st.text_input("Access Code", type="password")
    if st.button("Login"):
        if authenticate(email, code):
            if not validate_session(email, st.session_state["session_id"]):
                session_id = create_session(email)
                st.session_state["authenticated"] = True
                st.session_state["email"] = email
                st.session_state["session_id"] = session_id
                st.success("Authentication successful!")
            else:
                st.error("This email is already logged in from another session.")
        else:
            st.error("Invalid email or access code")

if st.session_state["authenticated"]:
    if validate_session(st.session_state["email"], st.session_state["session_id"]):
        # Title
        st.title("CloudArch Designer")
        update_interaction()

        # Supported cloud providers
        cloud_providers = ["AWS", "Azure", "Google Cloud", "IBM Cloud", "Oracle Cloud"]

        # User inputs
        with st.form("architecture_form"):
            file_name = st.text_input("Provide a file name for the project. Warning: File name will be used as provided")
            title = st.text_input("Provide a title of your cloud system architecture and a brief description")
            selected_providers = st.multiselect("Select cloud providers", cloud_providers)
            resources = st.text_area("What are the resources used in this cloud system architecture?")
            clustering = st.text_area("How are these cloud provider resources clustered or grouped? Describe in detail.")
            relationships = st.text_area("Describe the relationships between these resources and clusters/groups")
            submitted = st.form_submit_button("Submit", on_click=update_interaction)

        # Handle form submission
        user_id = st.session_state["session_id"]
        if submitted:
            input_data = {
                "title": title,
                "resources": resources,
                "clustering": clustering,
                "relationships": relationships,
                "cloud_providers": selected_providers,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                "file_name": file_name + "_" + user_id
            }
            st.session_state["input_data"] = input_data
            st.session_state["output"] = LLMInference().run_inference_openai(input_data)   # OpenAI inference
            # st.session_state["output"] = LLMInference().run_inference_openai(input_data)   # Google gemini inference     
            st.session_state["submitted"] = True

        # Display generated PNG and provide options if submitted
        if st.session_state["submitted"]:
            st.image(st.session_state["output"]["png_path"])
            update_interaction()
            
            if st.button("Regenerate", on_click=update_interaction):   #
                # st.session_state["output"] = LLMInference().run_inference_openai(st.session_state["input_data"])    # OpenAI inference
                st.session_state["output"] = LLMInference().run_inference_google(st.session_state["input_data"])  # Google Inference
                st.image(st.session_state["output"]["png_path"])
                st.experimental_rerun()    
            if st.button("Import to DrawIO", on_click=update_interaction):
                with open(st.session_state["output"]["drawio_path"], "rb") as f:
                    st.download_button(
                        label="Download DrawIO File",
                        data=f,
                        file_name=f"{st.session_state['input_data']['file_name']}.drawio",
                        mime="application/octet-stream"
                    )
            
            if st.button("Restart", on_click=update_interaction):
                files_to_remove = [
                    f"{st.session_state['input_data']['file_name']}.drawio",
                    f"{st.session_state['input_data']['file_name']}.png",
                    f"{st.session_state['input_data']['file_name']}.dot",
                    f"{st.session_state['input_data']['file_name']}"
                ]
                cleanup_files(files_to_remove)
                st.session_state["submitted"] = False
                st.session_state["output"] = None
                st.session_state["input_data"] = None
                st.experimental_rerun()

        if st.button("Logout"):
            terminate_session(st.session_state["email"])
            st.session_state["authenticated"] = False
            st.session_state["email"] = None
            st.session_state["session_id"] = None
            st.experimental_rerun()

        # Check idle time
        check_idle_time()
    else:
        st.error("Session expired or invalid. Please log in again.")
        st.session_state["authenticated"] = False
        st.session_state["email"] = None
        st.session_state["session_id"] = None





