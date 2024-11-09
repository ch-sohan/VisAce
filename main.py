from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import List

app = FastAPI()

# CORS middleware to allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing, change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the input model for visa type and country
class VisaDetails(BaseModel):
    visa_type: str
    country: str
    response: List[str]
    
# Example questions based on visa type and country
questions_db = {
    "student": {
        "USA": ["Why do you want to study in the USA?", "What is your chosen major?"],
        "UK": ["Why did you choose the UK for higher studies?", "Which university are you applying to?"]
    },
    "work": {
        "USA": ["What is your job role?", "How does your work contribute to the company?"],
        "UK": ["What skills do you bring to the UK?", "Describe your professional experience."]
    }
}

# Route to accept visa details and return questions
@app.post("/questions/") 
def get_questions(visa_details: VisaDetails):
    visa_type = visa_details.visa_type.lower()
    country = visa_details.country.upper()

    # Fetch questions from database or use default questions if not found
    questions = questions_db.get(visa_type, {}).get(country, ["What is your purpose for visiting?", "How long do you plan to stay?"])
    
    return {"questions": questions}

@app.post("/feedback/")
def get_feedback(visa_details: VisaDetails):
    visa_type = visa_details.visa_type.lower()
    country = visa_details.country.upper()
    response = visa_details.response
        
        # Constructing the initial prompt for the Gemini API
    prompt = (
        "You are an AI evaluating responses in a visa mock interview. "
        "The applicant is applying for a " + visa_type + " visa to " + country + ". "
        "They provided the following responses during the interview:\n"
    )

    # Adding user responses to the prompt
    prompt += "\n".join([f"Q{index + 1}: {resp}" for index, resp in enumerate(response)])

    # Adding analysis criteria and instructions
    prompt += (
        "\n\nAnalyze the applicant's answers based on the following criteria:\n"
        "1. Clarity: Is the response clear and easy to understand?\n"
        "2. Relevance: Does the response directly address the question asked?\n"
        "3. Persuasiveness: Does the response help the applicant's case for obtaining the visa?\n"
        "4. Improvement Suggestions: Provide advice on how the applicant can improve their answers to increase their chances of visa approval.\n\n"
        "Give feedback on each response in a structured format:\n"
        "- Response to Question 1:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
        "- Response to Question 2:\n  - Clarity:\n  - Relevance:\n  - Persuasiveness:\n  - Improvement Suggestions:\n"
        # Continue this pattern for all questions
        "Please provide detailed feedback for each response."
    )

    
    genai.configure(api_key=os.environ["API_KEY"])
    
    # Call the Gemini API to generate feedback
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(prompt)
        feedback = result.text
        print(result)
        return {"feedback": feedback}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
