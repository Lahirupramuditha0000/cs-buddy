import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai

# --- Configuration and Initialization ---

load_dotenv()
try:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    gen_ai.configure(api_key=API_KEY)
except ValueError as e:
    st.error(f"Configuration Error: {e}. Please ensure GOOGLE_API_KEY is set in your .env file.")
    st.stop()

try:
    MODEL = gen_ai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Error loading Gemini model: {e}. Please check your API key and model name.")
    st.stop()

# --- Streamlit Page Setup ---

st.set_page_config(
    page_title="CS Buddy 👩‍🏫",
    page_icon="💻",
    layout="centered"
)

# Custom CSS for a cleaner look
st.markdown("""
<style>
    /* Center the title and caption */
    .st-emotion-cache-1g8pjcj { /* Target for st.title */
        text-align: center;
    }
    .st-emotion-cache-10q7q2u { /* Target for st.caption */
        text-align: center;
    }

    /* Adjust chat bubble padding for a softer look */
    .st-emotion-cache-1c7y2qn { /* User message bubble */
        padding: 10px 15px;
        border-radius: 15px;
    }
    .st-emotion-cache-1gh866c { /* Assistant message bubble */
        padding: 10px 15px;
        border-radius: 15px;
    }

    /* General text improvements for readability */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("👩‍🏫 CS Teacher Bot for 10-Year-Olds")
st.caption("Ask me anything about computers or coding — I’ll make it fun and easy!")

# Add a separator for visual clarity
st.markdown("---")

# --- System Prompt / Context ---

SYSTEM_PROMPT = (
    "You are Ironbrain’s ICT teacher — a super friendly, patient, and clear computer science teacher for kids. "
    "Your goal is to make learning about computers and coding fun and easy for 10-year-olds. "
    "Begin every conversation by saying:\n\n"
    "\"Hey kids! What's your IT-related problem today? Don’t worry — just ask it!\"\n\n"
    "When a child responds, first, rephrase their question in very simple terms, like you're talking to a 10-year-old. "
    "Then, provide a clear, kind, and fun explanation with absolutely no technical jargon. "
    "Never reveal that you are an AI or a bot. Always refer to yourself as Ironbrain’s ICT teacher. "
    "Always encourage them to ask anything about ICT. "
    "Maintain a kind, supportive, and encouraging tone, never making them feel bad for not knowing something."
)

# --- Chat Session Management ---

if "chat_session" not in st.session_state:
    st.session_state.chat_session = MODEL.start_chat(history=[])
    st.session_state.chat_session.send_message(SYSTEM_PROMPT)
    st.session_state.chat_history = [{"role": "assistant", "text": "Hey kids! What's your IT-related problem today? Don’t worry — just ask it!"}]
elif not st.session_state.chat_session.history:
    st.session_state.chat_session = MODEL.start_chat(history=[])
    st.session_state.chat_session.send_message(SYSTEM_PROMPT)
    st.session_state.chat_history = [{"role": "assistant", "text": "Hey kids! What's your IT-related problem today? Don’t worry — just ask it!"}]

# --- Display Chat History ---

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

# --- Handle User Input ---

user_input = st.chat_input("Ask me anything about computers or coding...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    try:
        response_stream = st.session_state.chat_session.send_message(user_input, stream=True)

        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.chat_history.append({"role": "assistant", "text": full_response})

    except Exception as e:
        st.error(f"An error occurred while getting a response: {e}")
        st.session_state.chat_history.append({"role": "assistant", "text": "Oops! Something went wrong. Can you please try asking again?"})