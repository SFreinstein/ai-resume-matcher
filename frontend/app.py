# frontend/app.py
import streamlit as st
import requests

# Configure backend URL
BACKEND_URL = "http://backend:8000"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "resume_id" not in st.session_state:
    st.session_state.resume_id = None

def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        data = {
            "username": email,
            "password": password
        }

        try:
            # DO NOT manually set headers — let requests handle it
            response = requests.post(f"{BACKEND_URL}/token", data=data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.session_state.token = token
                st.success("Logged in successfully!")
            else:
                st.error(f"Login failed: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Login request failed: {e}")

def register():
    st.subheader("Register")
    name = st.text_input("Name")
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        data = {"name": name, "email": email, "password": password}
        try:
            response = requests.post(f"{BACKEND_URL}/register", data=data)
            if response.status_code == 200:
                st.success("Registered successfully! Please login.")
            else:
                st.error("Registration failed")
        except requests.exceptions.RequestException as e:
            st.error(f"Registration request failed: {e}")

def upload_resume():
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "txt"])
    
    if uploaded_file and st.button("Upload"):
        if not st.session_state.token:
            st.warning("Please login first.")
            return

        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

        try:
            response = requests.post(
                f"{BACKEND_URL}/upload_resume",
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                resume_id = response.json().get("resume_id")
                st.session_state.resume_id = resume_id
                st.success(f"Resume uploaded! Resume ID: {resume_id}")
            else:
                st.error(f"Failed to upload resume. Server said: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Upload failed: {e}")

def get_matches():
    st.subheader("Job Matches")
    
    if not st.session_state.token:
        st.warning("Please login first.")
        return

    if st.session_state.resume_id is None:
        st.warning("Please upload a resume first.")
        return

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    payload = {"resume_id": st.session_state.resume_id}

    try:
        response = requests.post(
            f"{BACKEND_URL}/match_jobs",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if matches:
                for match in matches:
                    st.write(f"🔹 Job ID: {match['job_id']} — {match['title']} (Score: {match['score']:.2f})")
            else:
                st.write("No matches found.")
        else:
            st.error(f"Error retrieving matches: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"Match request failed: {e}")

def main():
    st.title("AI Resume Matcher")
    menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Upload Resume", "Job Matches"])
    
    if menu == "Login":
        login()
    elif menu == "Register":
        register()
    elif menu == "Upload Resume":
        upload_resume()
    elif menu == "Job Matches":
        get_matches()

if __name__ == "__main__":
    main()
