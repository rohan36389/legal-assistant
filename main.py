import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import yaml

# Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Load stories.yml
def load_stories(file_path):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error("stories.yml file not found!")
        return {}

# Load stories
stories_file_path = r"C:\Users\chinn\Rasa\data\stories.yml"
stories = load_stories(stories_file_path)

# Intent-response mapping
intent_response_mapping = {
    story["steps"][0]["intent"]: story["steps"][1]["action"]
    for story in stories.get("stories", [])
}

response_mapping = {
    "utter_greet": "Hello! Welcome to the Legal Chatbot. Ask me any legal questions!",
    "utter_goodbye": "Goodbye! Thanks for visiting. Come back anytime!",
    "utter_affirm": "Got it!",
    "utter_deny": "Alright, let me know if there's anything else.",
    "utter_ipc_420": "Section 420 deals with cheating and dishonestly inducing delivery of property.",
    "utter_ask_family_law": "Family law covers divorce, adoption, and domestic matters.",
    "utter_bail": "Bail is a legal process that allows a person accused of a crime to remain free until trial.",
}

# Determine question type
def get_question_type(question):
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening"]
    farewells = ["bye", "goodbye", "see you", "exit", "thank you", "thanks"]
    legal_keywords = [
        "law", "legal", "family law", "criminal law", "section", "IPC", "court", 
        "punishment", "procedure", "document", "legislation", "act", "regulation", 
        "bail", "contract", "rights", "judgment", "advocate", "constitution"
    ]
    
    q_lower = question.lower().strip()
    
    if q_lower in greetings:
        return "greeting"
    elif q_lower in farewells:
        return "farewell"
    elif any(k in q_lower for k in legal_keywords):
        return "legal"
    else:
        return "non-legal"

# Set up Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

st.title("Legal Chatbot")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat messages
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

# Chat input
user_question = st.chat_input("Ask a legal question (or type 'bye' to exit):")

if user_question:
    question_type = get_question_type(user_question)

    if question_type == "greeting":
        response = response_mapping["utter_greet"]

    elif question_type == "farewell":
        response = response_mapping["utter_goodbye"]

    elif question_type == "legal":
        # Try to match an intent
        detected_intent = next(
            (intent for intent in intent_response_mapping.keys() if intent.lower() in user_question.lower()), None
        )
        if detected_intent:
            action = intent_response_mapping.get(detected_intent)
            response = response_mapping.get(action, "I don't have an answer for that.")
        else:
            prompt = f"You are a legal assistant. Answer concisely: {user_question}"
            gemini_response = model.generate_content(prompt)
            response = gemini_response.text

    else:
        response = "Please ask about legal matters."

    st.session_state.chat_history.append({"role": "user", "content": user_question})
    st.session_state.chat_history.append({"role": "assistant", "content": response + "\nDo you have any other legal questions?"})

    with st.chat_message("assistant"):
        st.write(response + "\nDo you have any other legal questions?")