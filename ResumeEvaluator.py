import re
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from model_test import predict_tone

class VideoResumeEvaluator:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        """
        Initialize the evaluator with the specified LLM model and
        preserve the new functionality (cleaning + tone analysis).
        """
        # 1. Initialize the LLM (as in the old code)
        self.llm = ChatGroq(
            model=model_name,
            api_key="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"
        )
        self.output_parser = StrOutputParser()

        # 2. Define the prompt for the LLM
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system", 
                "You are an expert interviewer. You are evaluating a video resume based on a given transcription.\n"
                "Give the detailed explanation of your response"
            ),
            (
                "user",
                """Transcription: {transcription_input}

Questions:
1. Was the content interesting and as per the guidelines provided? (Yes/No, Don't give any Explanation)
2. Who are you and what are your skills, expertise, and personality traits? (Rate: Needs Improvement, Poor, Satisfactory, Excellent) (Only Rate it, Don't give any Explanation)
3. Why are you the best person to fit this role? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
4. How are you different from others? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
5. What value do you bring to the role? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
6. Did the speech have a structure of Opening, Body, and Conclusion? (Single line descriptive answer)
7. How was the quality of research for the topic? Did the student’s speech demonstrate a good depth? Did they cite sources of research properly? (2-3 lines descriptive answer)
8. How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity? (Descriptive answer)

Only answer these questions. Don't write anything extra except these answers, and start with 'These are the Answers:'
"""
            )
        ])

        # 3. Build the chain (PromptTemplate → LLM → Parser)
        self.chain = self.prompt_template | self.llm | self.output_parser

    def clean_transcription(self, text: str) -> str:
        """
        Removes transcript timestamps like [0.00s - 9.00s] and extra spacing.
        """
        cleaned_text = re.sub(r'\[\d+\.\d+s\s*-\s*\d+\.\d+s\]', '', text)
        return ' '.join(cleaned_text.split())

    def evaluate_transcription(self, transcription_data):
        """
        1. Cleans the transcription text.
        2. Runs tone analysis.
        3. Invokes the LLM pipeline using the same prompt structure.
        4. Returns a dict with both the LLM output and the tone analysis.
        """
        # 1. Extract & clean text
        if isinstance(transcription_data, dict):
            text = transcription_data.get('text', '')
        else:
            text = transcription_data
        
        if not text.strip():
            raise ValueError("Transcription text must not be empty.")
        
        cleaned_text = self.clean_transcription(text)

        # 2. Get tone analysis
        tone_results = predict_tone(cleaned_text)

        # 3. Invoke the LLM pipeline
        llm_output = self.chain.invoke({
            "transcription_input": cleaned_text
        })

        # 4. Return combined results
        return {
            "content_evaluation": llm_output,
            "tone_analysis": tone_results
        }