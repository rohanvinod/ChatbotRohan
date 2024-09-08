from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import shelve
#import easyocr
#from googletrans import Translator
#from gtts import gTTS
#from PIL import Image
#import numpy as np

load_dotenv()

st.title("Rohan's Chatbot Interface")

USER_AVATAR = "🧑🏾"
BOT_AVATAR = "🤖"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# If openai model is not initiated on startup, then initiate
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# Load all the chat history from the shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])


# Save chat history to the shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages


# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

#Connects to CSS file which regulates the size of the sidebar buttons
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

#These are the language selection menus on the sidebar for translation
st.sidebar.title('Language Selection Menu')
#st.sidebar.subheader('Select...')
src = st.sidebar.selectbox("From Language",['English','Spanish','Arabic','Tamil'])

#st.sidebar.subheader('Select...')
destination = st.sidebar.selectbox("To Language",['Spanish','Arabic','Tamil','English'])

st.sidebar.subheader("Enter Text to Translate")
area = st.sidebar.text_area("","")

helper = {'Tamil':'ta','Spanish':'sp','English':'en','Arabic':'ar'}
dst = helper[destination]
source = helper[src]

if st.sidebar.button("Translate"):
    if len(area)!=0:
        sour = translator.detect(area).lang
        answer = translator.translate(area, src=f'{sour}', dest=f'{dst}').text
        #st.sidebar.text('Answer')
        st.sidebar.text_area("Answer",answer)
        st.balloons()
    else:
        st.sidebar.subheader('Enter Text!')

# Sidebar with a button to clear all previous chat history
with st.sidebar:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        save_chat_history([])

#sidebar with a button to upload images, with the code to access files to upload an image into the chat
with st.sidebar:
    if st.button("Upload Image"):
        #st.session_state.messages = []
        img_file_buffer = st.file_uploader('Upload a PNG image', type='png')
        if img_file_buffer is not None:
            image = Image.open(img_file_buffer)
            img_array = np.array(image)



# Display chat messages in the interface
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# This code represents the main chat interface
if prompt := st.chat_input("How may I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
