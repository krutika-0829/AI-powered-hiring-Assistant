import requests

OLLAMA_URL =  "http://localhost:11434/api/generate"

def req_llm(prompt):
    response = requests.post(
       OLLAMA_URL,json={
           "model" : "mistral",
           "prompt" : prompt,
           "stream" : False
       }
    )
    return response.json()["response"]



def get_information(cleaned_text):
    prompt = f"""
    You are an AI hiring assistant.

    Extract candidate information from the resume text.

    Return ONLY valid JSON.

    IMPORTANT RULES:
    
    - Extract the Candidates's actual full name.
    - Do NOT invent information.
    - If a field is missing, return an empty string.
    - Skills should be a list.
    - Projects should be a list.
    - Infer the candidate's job role from their experience,If unclear return null.

    Return JSON in EXACTLY this format:

    {{
      "Name": "...",
      "Education": "...",
      "Skills": [],
      "Experience": "...",
      "Projects": [],
      "Role" : "..."
    }}

    Example output:
    {{
     "Name": "John Smith",
     "Education": "B.Tech in Computer Science, MIT (2020-2024)",
     "Skills": ["Python", "Machine Learning", "SQL"],
     "Experience": "Software Engineer at Google (2024)",
     "Projects": ["AI Chatbot", "Search Engine"],
     "Role" : "Software Engineer"
    }}
    
    Resume Text:
    {cleaned_text}
    
    Rules:
    - No extra text
    - Only JSON output
    - Do not assume information
    - No comments
    - Skills must be a list, use [] if none
    - Projects must be a list, use [] if none
    - Name, Education, Experience use null if not found
    - Copy text exactly, do not paraphrase
    """
    return req_llm(prompt)


def query_filter(query):
    prompt = f"""
You are an information extraction system for a resume search engine.

Your task is to extract structured filter criteria from the user's query.

Return ONLY valid JSON. Do not explain anything.

### Rules:
- If a field is not mentioned, set it to null.
- Do NOT assume values unless they are strongly implied.
- Normalize synonyms (e.g., "dev" → "developer", "ML" → "machine learning").
- Extract even partial signals (e.g., "Python backend" → skills: ["python"], role: "backend").
- Be robust to informal language.
- Ignore filler words.

### Output schema:
{{
  "skills": [],
  "projects" : [],
  "role": null,
  "education": null,
  "company": null,
  "keywords": []
}}

### Field rules:
- skills: technical + soft skills explicitly or implicitly mentioned
- projects: project names, domains, systems, applications, or implementation areas mentioned in the query
- role: job title or function (e.g. backend engineer, data scientist)
- education: degree or qualification
- company: target or past company names
- keywords: any other useful search terms

### Examples:

Input: "Python dev with  experience in backend systems"
Output:
{{
  "skills": ["python"],
  "projects": ["chatbot", "rag"],
  "role": "backend developer",
  "education": null,
  "company": null,
  "keywords": ["backend systems"]

}}



Now process this query:
{query}
"""
    return req_llm(prompt)


def QnA(user_input,retrived_context):
    prompt = f""" You are a hiring Assitant for recruiting team
    Your job is to answer the Question asked
    
    Answer ONLY using information explicitly present in the Retrieved Context.
    Do not infer, assume, or fabricate missing details.

  #Answering Guidelines:
    -Provide concise but complete answers strictly supported by the retrieved context.
    - Do NOT return short phrases.
    - If the answer involves a person, include the person's name.
    - Prefer full sentences over fragments.
    - Be specific and explicit.
    - mention candidates name if asked 

  # Examples
    Question:
    ,bfkf.bk
    Output:
    {{
      "Answer": "Invalid or unclear query"
    }}

    Question:
    Does Rahul know Kubernetes?

    Retrieved Context:
    Rahul knows Python and FastAPI.
    Output:
    {{
      "Answer": "Information not found in resume"
    }}

    Question:
    What projects has Rahul worked on?
    Retrieved Context:
    Rahul built an AI Email Assistant and Semantic Search Engine.
    Output:
    {{
      "Answer": "Rahul worked on an AI Email Assistant and a Semantic Search Engine."
    }}
    Question:
      {user_input}

    Retrieved Context:
      {retrived_context}

    Return JSON FORMAT ONLY :
    {{
    "Answer" : "..." 
    }}
   
    If the question is unclear or gibberish, return:
    {{"Answer": "Invalid or unclear query"}}

    If answer is not found in provided context,
    return:
    {{
       "Answer": "Information not found in resume"
    }}

    Rules:
    - No extra text
    - Only JSON output
    - Use only the retrieved context
    - Do not assume information
    """
    return req_llm(prompt)










