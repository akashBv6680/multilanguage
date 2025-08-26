import streamlit as st
import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

# Set Streamlit page configuration
st.set_page_config(page_title="Multilingual LLM Chatbot", layout="wide")

# Add a title and introductory text
st.title("Multilingual LLM Chatbot 🤖💬")
st.info("Ask me anything! I can understand and reply in English, Tamil, French, and many other languages.")

# --- Model Loading ---
@st.cache_resource(show_spinner=False)
def get_model_and_tokenizer():
    # Use a powerful, multilingual model
    model_id = "google/gemma-2b-it" 
    
    # Load the tokenizer and model.
    # We now pass the Hugging Face token from Streamlit's secrets.
    # The 'HUGGINGFACE_TOKEN' secret is required for gated models.
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=st.secrets["HUGGINGFACE_TOKEN"])
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        token=st.secrets["HUGGINGFACE_TOKEN"]
    )
    return tokenizer, model

tokenizer, model = get_model_and_tokenizer()

# --- Session State and UI Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": "You are a helpful and polite multilingual assistant. Reply to user questions in the language they use."})

# Display chat messages from history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    chat = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
    tokenized_chat = tokenizer.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    tokenized_chat = tokenized_chat.to(model.device)
    
    with st.spinner("Thinking..."):
        outputs = model.generate(tokenized_chat, max_new_tokens=256)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    assistant_text = re.search(r'<end_of_turn>model\s*(.*?)(?:<end_of_turn>|$)', response_text, re.DOTALL).group(1).strip()
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
