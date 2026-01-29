#python3 -m streamlit run ai-agents/demo0.py --server.port 8501 --server.headless true
# Step 0: Import libraries
from dotenv import load_dotenv
import os
import streamlit as st
from pydantic import BaseModel
import openai
from openai import OpenAI
# Step 1: Load environment variables
# Load variables from .env if present (not required for Ollama).
load_dotenv()
# Connect to the client


from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")



# Step 3: Build Streamlit UI
# Use Streamlit to create a simple UI where users can input their question and get a structured response.
st.title("Web Search Optimization with LLM (Ollama)")
st.write("Enter a question to receive an optimized web search query and reasoning.")
user_query = st.text_input("Enter your question")


# Step 5: Process the query
if user_query:
    response = client.chat.completions.create(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": user_query}],
        temperature=0.3,
    )
    response_content = response.choices[0].message.content
    # Display the result in our interface
    st.write("Model output")
    st.write(response_content)