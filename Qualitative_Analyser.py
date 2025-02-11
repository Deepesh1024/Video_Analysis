import re
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
import json
class VideoResumeEvaluator2:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        """
        Initialize the evaluator with the specified LLM model and
        preserve the new functionality (cleaning + tone analysis).
        """
        
        self.llm = ChatGroq(
            model=model_name
        )
        self.output_parser = JsonOutputParser()
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system", 
                "You are an expert interviewer. You are evaluating a video resume based on a given transcription.\n"
                "Give the detailed explanation of your response"
            ),
            (
                "user",
                """Transcription: {transcription_input}

You have to Evaluate Candiate's Performance based on two criteria's Qualitative Analysis and Quantitative Analysis 
you will be provided with the transcription of the candidate, 
Give at least 3 points in the Section of Qualitative Analysis make it clear and concise, in qualitative analysis, you have to talk about the Positives of the candidate
Give your answers in this format (e.g : You delivered the presentation with a clear voice and tone, Your articulation was up to the mark, Avoid using sentences like “Leading a team is just logistics”. This comes across as not being interested in
taking on leadership roles at all.
, Overall a very confident presentation.) You can directly Point out the user, in whichever point you want. 
and in case of Quantitative Analysis, Give atleast 5 points, make it clear and concise, In Quantitative Analysis, talks about the Areas of Improvement, Talk About where user can improve, and give your output finally in dictionary format something like this. Also When Talking About Areas of Improvement, if there is a Rude Sentence, or a sentence that should not be said, point it in the Quantitative Analysis One, 
In a json file Key => Qualitative Analysis , Value = (your answer in points) Similarly, key = Quantitative Analysis , Value = (your answer in points) , No extras, i only the dictionary Output, Remember this very Carefully, and also You are not allowed to talk about the feature, which you don't know, like you can't talk 
about his tone, posture, because you don't know about this, but you have the transcription, so try to give the points only on those basis . 
"""
            )
        ])
        self.chain = self.prompt_template | self.llm | self.output_parser

    def clean_transcription(self, text: str) -> str:
        """
        Removes transcript timestamps like [0.00s - 9.00s] and extra spacing.
        """
        cleaned_text = re.sub(r'\[\d+\.\d+s\s*-\s*\d+\.\d+s\]', '', text)
        return ' '.join(cleaned_text.split())

    def evaluate_transcription(self, transcription_data):
        if isinstance(transcription_data, dict):
            text = transcription_data.get('text', '')
        else:
            text = transcription_data
        
        if not text.strip():
            raise ValueError("Transcription text must not be empty.")
        
        cleaned_text = self.clean_transcription(text)

       
        llm_output = self.chain.invoke({
            "transcription_input": cleaned_text
        })

        with open('json/quality_analysis.json' , 'w') as fp:
            json.dump(llm_output , fp)

        return llm_output
        