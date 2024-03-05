import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging


# Load JSON File.
with open(
    "/home/tutorial1/keusu/Documents/python_gen_ai/mcgen/Response.json", "r"
) as file:
    RESPONSE_JSON = json.load(file)

# Create Title for the App
st.title("MCQs Creator Application with Langchain.")

# Create a Form
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])

    # Input Fields
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50)

    # Subject
    subject = st.text_input("Insert Subject", max_chars=20)

    # Quiz Tone
    tone = st.text_input(
        "Complexity Level of Questions", max_chars=20, placeholder="Simple"
    )

    # Add Button
    button = st.form_submit_button(label="Generate MCQs")

    # Check if the button has been clicked and all fields have inputs.

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                text = read_file(uploaded_file)
                # Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON),
                        }
                    )
                    # st.write(response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error generating MCQs. Please try again.")

            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response, dict):
                    # Extract the Quiz Data from the Response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            # Display the Review in a Text Box as well.
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the Table Data.")
                
                else:
                    st.write(response)
                        
