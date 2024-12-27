import streamlit as st
import google.generativeai as genai
import os
import fitz
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.secrets("GOOGLE_API_KEY")

specialties = {
    "Cardiologist": [
        {"name": "Dr. Alice Heart", "time_slots": ["10:00 AM", "2:00 PM"]},
        {"name": "Dr. Bob Cardio", "time_slots": ["11:00 AM", "4:00 PM"]},
    ],
    "Dermatologist": [
        {"name": "Dr. Clara Skin", "time_slots": ["9:00 AM", "3:00 PM"]},
        {"name": "Dr. David Derma", "time_slots": ["12:00 PM", "5:00 PM"]},
    ],
    "Pediatrician": [
        {"name": "Dr. Emily Kids", "time_slots": ["10:30 AM", "1:30 PM"]},
        {"name": "Dr. Frank Child", "time_slots": ["11:30 AM", "3:30 PM"]},
    ],
}

def generate_healthcare_response(user_input):
    restrictive_prompt = f"""
    You are a healthcare assistant trained to provide information and assistance strictly related to healthcare.
    User's Query: {user_input}
    Your Response:
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([restrictive_prompt])
    return response.text



def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # Open the uploaded PDF file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in pdf_document:  # Loop through all pages
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"



def summarize_lab_report(text):
    prompt = f"""
    You are a medical assistant specialized in summarizing lab test reports.

    Guidelines:
    1. Summarize the key points of the lab test report provided.
    2. Highlight any significant results or abnormalities and their potential implications.
    3. Clearly mention the test results, the normal reference range, and whether the results fall within or outside this range.
    4. Use clear, concise, and easy-to-understand language.
    5. Provide general suggestions on what these results could indicate, but avoid making a medical diagnosis.
    6. Encourage consulting a doctor or healthcare professional for a detailed interpretation and next steps.

    Lab Report Content:
    {text}

    Summary:
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt])
    return response.text


if "chat_stage" not in st.session_state:
    st.session_state["chat_stage"] = "main_menu"
if "selected_specialty" not in st.session_state:
    st.session_state["selected_specialty"] = None
if "selected_doctor" not in st.session_state:
    st.session_state["selected_doctor"] = None
if "selected_time" not in st.session_state:
    st.session_state["selected_time"] = None
if "medications" not in st.session_state:
    st.session_state["medications"] = []

st.set_page_config(page_title="AI Healthcare Chatbot", layout="centered")
st.title("🤖 AI Healthcare Assistant")
st.markdown("---")

def show_progress(step, total_steps):
    st.progress(step / total_steps)

st.sidebar.title("⚙️ Navigation")
selected_tab = st.sidebar.radio("Choose an Option", ["Home", "Ask a Medical Question", "Book an Appointment", "Medication Reminders","Lab Test Assistance"])

if selected_tab == "Home":
    st.subheader("👋 Welcome to the AI Healthcare Chatbot!")
    st.write("""
    I can assist you with:
    - **Medical Questions**: Ask about symptoms, diseases, or health advice.
    - **Booking Appointments**: Schedule a visit with a specialist.
    - **Medication Reminders**: Set reminders for your medications.
    - **Lab Test Assistance**: Upload lab test reports for a summary.
    """)
    st.info("Use the **Navigation Bar** on the left to get started!")

elif selected_tab == "Ask a Medical Question":
    st.subheader("🩺 Ask a Medical Question")
    st.write("**Enter your health-related query below:**")
    user_query = st.text_input("What would you like to know?")
    if user_query:
        with st.spinner("Thinking... 🤖"):
            response = generate_healthcare_response(user_query)
        st.success("Here’s what I found:")
        st.write(response)

elif selected_tab == "Book an Appointment":
    st.subheader("📅 Book an Appointment")
    step = 0
    total_steps = 3

    if not st.session_state["selected_specialty"]:
        st.write("**Step 1: Choose a Specialty**")
        specialty = st.radio("Select a specialty:", list(specialties.keys()))
        if st.button("Next"):
            st.session_state["selected_specialty"] = specialty
            step += 1
        show_progress(step + 1, total_steps)

    if st.session_state["selected_specialty"] and not st.session_state["selected_doctor"]:
        st.write("**Step 2: Choose a Doctor**")
        doctors = specialties[st.session_state["selected_specialty"]]
        for idx, doctor in enumerate(doctors):
            st.write(f"**{doctor['name']}** - Available slots: {', '.join(doctor['time_slots'])}")
            if st.button(f"Select {doctor['name']}", key=f"doctor_{idx}"):
                st.session_state["selected_doctor"] = doctor
        show_progress(step + 2, total_steps)

    if st.session_state["selected_doctor"] and not st.session_state["selected_time"]:
        st.write(f"**Step 3: Choose a Time Slot for {st.session_state['selected_doctor']['name']}**")
        for time in st.session_state["selected_doctor"]["time_slots"]:
            if st.button(time):
                st.session_state["selected_time"] = time
        show_progress(step + 3, total_steps)

    if st.session_state["selected_time"]:
        st.success("✅ Appointment Details:")
        st.write(f"- **Specialty:** {st.session_state['selected_specialty']}")
        st.write(f"- **Doctor:** {st.session_state['selected_doctor']['name']}")
        st.write(f"- **Time Slot:** {st.session_state['selected_time']}")
        if st.button("Confirm Appointment"):
            # st.balloons()
            st.success("🎉 Your appointment has been successfully booked!")
            st.session_state["selected_specialty"] = None
            st.session_state["selected_doctor"] = None
            st.session_state["selected_time"] = None

elif selected_tab == "Medication Reminders":
    st.subheader("💊 Medication Reminders")
    med_name = st.text_input("Enter medication name:")
    time = st.time_input("Set reminder time:")
    if st.button("Add Reminder"):
        st.session_state["medications"].append({"name": med_name, "time": str(time)})
        st.success(f"Reminder for **{med_name}** set at {time}!")
    if st.session_state["medications"]:
        st.write("### Your Medication Reminders:")
        for med in st.session_state["medications"]:
            st.write(f"- **{med['name']}** at {med['time']}")
    if st.button("Clear All Reminders"):
        st.session_state["medications"] = []
        st.success("All reminders have been cleared.")

elif selected_tab == "Lab Test Assistance":
    st.subheader("📑 Lab Test Assistance")
    st.write("Upload your lab test report (PDF), and I will summarize it for you.")
    
    uploaded_file = st.file_uploader("Upload Lab Test Report", type=["pdf"])
    
    if uploaded_file is not None:
        st.info("📤 File uploaded successfully. Extracting content...")
        with st.spinner("Analyzing your lab report..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            if extracted_text:
                summary = summarize_lab_report(extracted_text)
                st.success("✅ Here's the summary of your lab report:")
                st.write(summary)
            else:
                st.error("Could not extract text. Ensure the file is a readable PDF.")

st.markdown("---")
st.caption("🤖 AI Healthcare Assistant | © 2024")
