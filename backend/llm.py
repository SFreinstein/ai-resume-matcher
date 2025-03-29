import requests
from config import GEMINI_API_KEY

def compute_similarity(resume_text: str, job_text: str) -> float:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = (
        "Rate the similarity between the following resume and job description from 0.0 to 1.0. "
        "Only respond with a number.\n\n"
        f"Resume:\n{resume_text[:1500]}\n\nJob:\n{job_text[:1500]}\n\nScore:"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        score_str = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return float(score_str.strip())
    except Exception as e:
        print("⚠️ Gemini API error:", e)
        return 0.0
