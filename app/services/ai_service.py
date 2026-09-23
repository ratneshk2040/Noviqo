import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

# Environment variables load karein
load_dotenv(override=True)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_client() -> OpenAI:
    """Fetch the latest API key at request time."""
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or not api_key.startswith("sk-"):
        raise RuntimeError("OpenAI API key is not configured. Check your .env file.")

    return OpenAI(api_key=api_key)


def clean_json_string(raw: str) -> str:
    if not raw:
        return ""

    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)

    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].lstrip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return cleaned


def call_openai_chat(messages: List[Dict], model: str = OPENAI_MODEL) -> str:
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
        content = response.choices[0].message.content
        if not content:
            return ""
        return str(content).strip()

    except Exception as error:
        raise RuntimeError(f"OpenAI request failed: {error}")


def explain_question(question_text: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant for government exam preparation."
        },
        {
            "role": "user",
            "content": f"""
Explain this question in simple language.

Provide:
1. Explanation
2. Correct answer
3. Why other options are wrong
4. Important points
5. Short notes
6. One line revision summary

Question:
{question_text}
"""
        }
    ]

    try:
        result = call_openai_chat(messages)
        if not result:
            raise RuntimeError("Empty OpenAI response")

        return {
            "explanation": result,
            "answer": "Refer to AI explanation for correct answer.",
            "wrong_options": "Refer to explanation.",
            "important_points": result,
            "short_notes": result,
            "one_line": result
        }

    except Exception as error:
        print("OPENAI ERROR:", error)
        return {
            "explanation": "AI explanation is currently unavailable. Please check your OpenAI API key or credit balance.",
            "answer": "N/A",
            "wrong_options": "N/A",
            "important_points": "N/A",
            "short_notes": (question_text[:120] + "...") if question_text else "AI notes unavailable",
            "one_line": "Pending AI generation."
        }


def generate_mcq(question_text: str, correct_answer: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": "You are an expert exam question creator."
        },
        {
            "role": "user",
            "content": f"""
Create a multiple choice question.

Return ONLY valid JSON.

Format:
{{
"question_text":"",
"options":[
{{"label":"A","text":""}},
{{"label":"B","text":""}},
{{"label":"C","text":""}},
{{"label":"D","text":""}}
],
"correct_option":"A"
}}

Question:
{question_text}

Correct Answer:
{correct_answer}

Create three wrong but realistic options.
"""
        }
    ]

    try:
        response = call_openai_chat(messages)
        payload = clean_json_string(response)
        if not payload:
            raise ValueError("Empty model payload")
        parsed = json.loads(payload)

        if not isinstance(parsed, dict):
            raise ValueError("OpenAI response is not a JSON object")

        if "options" not in parsed or not isinstance(parsed["options"], list):
            raise ValueError("OpenAI response missing valid options list")

        return parsed

    except Exception:
        return {
            "question_text": question_text,
            "options": [
                {"label": "A", "text": correct_answer},
                {"label": "B", "text": "Incorrect option"},
                {"label": "C", "text": "Related concept"},
                {"label": "D", "text": "Wrong answer"}
            ],
            "correct_option": "A"
        }