import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Set Streamlit page configuration
st.set_page_config(page_title="Multilingual LLM Chatbot", layout="wide")

st.title("Multilingual Chatbot 🤖💬")
st.info("I am a single chatbot that understands and replies in English, Tamil, French, Japanese, and more!")

# --- Model Loading ---
@st.cache_resource(show_spinner="Loading model...")
def get_model_and_tokenizer():
    # Use a single, instruction-tuned multilingual model
    model_id = "google/gemma-2b-it"  # A great, efficient choice for multi-language chat
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    return tokenizer, model

tokenizer, model = get_model_and_tokenizer()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a system message to guide the model's behavior
    st.session_state.messages.append({"role": "system", "content": "You are a helpful and polite multilingual assistant. Respond in the language of the user."})

# Display chat messages from history
for message in st.session_s
tate.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the chat history for the model
    chat = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
    
    tokenized_chat = tokenizer.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    tokenized_chat = tokenized_chat.to(model.device)
    
    with st.spinner("Thinking..."):
        outputs = model.generate(tokenized_chat, max_new_tokens=256)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    # Extract the assistant's reply
    import re
    assistant_text = re.search(r'<end_of_turn>model\s*(.*?)(?:<end_of_turn>|$)', response_text, re.DOTALL).group(1).strip()
    
    # Add assistant's reply to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
    
    with st.chat_message("assistant"):
        st.markdown(assistant_text)
