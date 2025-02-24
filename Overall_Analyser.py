from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_groq import ChatGroq


class VideoResumeEvaluator:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        """Initialize the evaluator with the specified LLM model."""
        self.llm = ChatGroq(model=model_name, api_key = "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")
        self.output_parser = StrOutputParser()
        
        # Define the prompt for the LLM
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert interviewer. You are evaluating a video resume based on a given transcription. Answer the following questions:"),
                ("user", 
                 """
                 Transcription: {transcription_input}

                 Questions:
                 1. Did the Speaker Speak with confidence ? (Give the One Line Answer)
                 2. Was the content interesting and as per the guidelines provided? (Yes/No, Don't give any Explanation)
                 3. Who are you and what are your skills, expertise, and personality traits? (Rate: Needs Improvement, Poor, Satisfactory, Excellent) (Only Rate it, Don't give any Explanation)
                 4. Why are you the best person to fit this role? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
                 5. How are you different from others? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
                 6. What value do you bring to the role? (Rate: Excellent, Good, Poor) (Only Rate it, Don't give any Explanation)
                 7. Did the speech have a structure of Opening, Body, and Conclusion? (Single line descriptive answer)
                 8. How was the quality of research for the topic? Did the student’s speech demonstrate a good depth? Did they cite sources of research properly? (2-3 lines descriptive answer)
                 9. How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity? (Descriptive answer)
                 Only Answer these Questions, Don't write anything Extra Except Answers of these, Start with These are the Answers, and simply Write all the Answers one by one.
                 """
                )
            ]
        )
        
        
        self.chain = self.prompt_template | self.llm | self.output_parser

    def evaluate_transcription(self, transcription):
        """Evaluate the provided transcription and return the LLM's response."""
        if not transcription:
            raise ValueError("Transcription must not be empty.")
        
        # Run the chain with the transcription input
        output = self.chain.invoke({
            'transcription_input': transcription
        })
        
        return output