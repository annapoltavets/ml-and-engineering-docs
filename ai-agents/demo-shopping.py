import os
import streamlit as st

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from pydantic import BaseModel
from langchain.schema import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser


load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

st.title("Shopping assistant")
st.write("What are you looking for?")
initial_query = st.text_input(key=0, label="e.g., a summer dress, a business suit, casual shoes...")

from langchain.schema import SystemMessage, HumanMessage

class StylistQuestions(BaseModel):
    questions: list[str]

    # Create a Pydantic output parser
output_parser = PydanticOutputParser(pydantic_object=StylistQuestions)



if initial_query:
    messages = [
        SystemMessage(content="Act as a personal stylist."),
        HumanMessage(content=f"How to find best: {initial_query}. Provide a step-by-step guide as a number of questions to ask the user to find the best outfit.")
    ]

    response = llm.invoke(input=messages, output_parser=output_parser)
    # Display the result in our interface
    st.write("I need a little bit more information to help you. Please answer the following questions:")

    additional_info = {}
    for q in response.questions:
        st.write(f"- {q}")
        additional_info[q] = st.text_input(label=q, key=q)
        st.write(additional_info[q])
        st.write("---")

    if all(additional_info.values()):
        answer_query = " ".join([f"{k}: {v}." for k, v in additional_info.items()])
        messages = [
            SystemMessage(content="Act as an independent shopping assistant and personal stylist."),
            HumanMessage(content=f"I am looking for: {initial_query}. They answered the following question: {answer_query}. Based on this, provide a final recommendation of what to buy and why.")
        ]

        response_content = llm.invoke(input=messages).content
        # Display the result in our interface
        st.write("Based on your answers, I recommend the following:")
        st.write(response_content)
