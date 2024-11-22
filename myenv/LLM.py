from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st

# Initialize the Streamlit app
st.title("Video Resume Evaluation")

# Text input: transcription from the video resume
transcription = st.text_area("Paste the transcription from the video resume:")

# Initialize LLM
llm = Ollama(model="llama3:8b")  # Ensure you are using the right model version
output_parser = StrOutputParser()

# Define the prompt for the LLM
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert interviewer. You are evaluating a video resume based on a given transcription. Answer the following questions:"),
        ("user", 
         """
         Transcription: {transcription_input}

         Questions:
         1. Was the content interesting and as per the guidelines provided? (Yes/No answer with reasoning)
         2. Who are you and what are your skills, expertise, and personality traits? (Rate: Excellent, Good, Poor) (Only Rate it, No Explanation)
         3. Why are you the best person to fit this role? (Rate: Excellent, Good, Poor) (Only Rate it, No Explanation)
         4. How are you different from others? (Rate: Excellent, Good, Poor) (Only Rate it, No Explanation)
         5. What value do you bring to the role? (Rate: Excellent, Good, Poor) (Only Rate it, No Explanation)
         6. Did the speech have a structure of Opening, Body, and Conclusion? (Single line descriptive answer)
         7. How was the quality of research for the topic? Did the student’s speech demonstrate a good depth? Did they cite sources of research properly? (2-3 lines descriptive answer)
         8. How convinced were you with the overall speech on the topic? Was it persuasive? Will you be consider them for the job/opportunity? (Descriptive answer)
         Only Answer these Questions, Don't write anything Extra Except Answers of these
         """
        )
    ]
)

# Create the chain to run the model and output parser
chain = prompt_template | llm | output_parser

# When transcription input is provided, process it
if transcription:
    # Run the chain with the transcription input
    output = chain.invoke({
        'transcription_input': transcription
    })
    
    # Display the LLM's responses in Streamlit
    st.write("Evaluation Results:")
    st.write(output)
