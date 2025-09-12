import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import yaml

# Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Load stories.yml and intents/responses
def load_stories(file_path):
    try:
        with open(file_path, "r") as file:
            stories = yaml.safe_load(file)
            return stories
    except FileNotFoundError:
        st.error("stories.yml file not found!")
        return {}

# Load stories file
stories_file_path = "path_to_your_stories.yml"  # Update this with the correct path
stories = load_stories(r"C:\Users\chinn\Rasa\data\stories.yml")

# Extract intents and responses from stories.yml
intent_response_mapping = {
story["steps"][0]["intent"]: story["steps"][1]["action"]
    for story in stories.get("stories", [])
}

response_mapping = {
    "utter_greet": "Hello! How can I assist you with legal queries today?",
    "utter_goodbye": "Goodbye! Feel free to return anytime for legal assistance.",
    "utter_affirm": "Got it!",
    "utter_deny": "Alright, let me know if there's anything else.",
    "utter_ipc_420": "Section 420 deals with cheating and dishonestly inducing delivery of property.",
    # Add all other mappings here based on your domain.yml responses
}

# Set up the Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

# Simple UI
st.title("Legal Assistant")

# Get user input
user_question = st.text_input("Ask a legal question:")

# Generate response when user submits a question
if st.button("Submit") and user_question:
    try:
# Check if the query matches any intent in stories.yml
        detected_intent = None
        for intent in intent_response_mapping.keys():
            if intent.lower() in user_question.lower():  # Simplistic intent detection
                detected_intent = intent
                break

        # Answer based on stories.yml if intent is found
        if detected_intent:
            action = intent_response_mapping.get(detected_intent)
            response = response_mapping.get(action, "I don't have a specific answer for this.")
            st.write("Response:")
            st.write(response)
        else:
            # Use Gemini API if no intent matches
            prompt = "You are a legal assistant who provides a short and concise answer for the user query: " + user_question
            gemini_response = model.generate_content(prompt)
            st.write("Response:")
            st.write(gemini_response.text)

    except Exception as e:
        st.error(f"Error: {str(e)}")