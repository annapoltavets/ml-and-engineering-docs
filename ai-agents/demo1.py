import openai
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from dataclasses import asdict, dataclass
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from openai import OpenAI
# OpenAI API setup (ensure you have your OpenAI API key set)
load_dotenv()
client = OpenAI(
  base_url="http://localhost:11434/v1", # Ollama's local HTTP API
  api_key="ollama"            # any non-empty string works locally
)