import logging
from itertools import cycle
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq client pool (same pattern as enricher.py, but sync)
keys = []
if settings.groq_api_keys:
    keys = [k.strip() for k in settings.groq_api_keys.split(",") if k.strip()]
elif settings.groq_api_key:
    keys = [settings.groq_api_key.strip()]

groq_clients = [Groq(api_key=k) for k in keys]
client_cycle = cycle(groq_clients) if groq_clients else None

MODEL_NAME = "llama-3.1-8b-instant"


def classify_query(question: str) -> str:
    """
    Classifies a query about a codebase into one of: 'lookup' | 'explanation' | 'architectural'.
    Uses llama-3.1-8b-instant via Groq. Defaults to 'explanation' on error.
    """
    if not client_cycle:
        logger.error("No Groq API keys available for classification.")
        return "explanation"

    system_prompt = "You are a code query classifier. Respond with exactly one word."
    user_prompt = f"""Classify this question about a codebase into one category:
 - lookup: asking for a specific value, definition, or location
   (e.g. 'where is X defined', 'what does constant Y equal')
 - explanation: asking how something works
   (e.g. 'how does X work', 'what does function Y do')
 - architectural: asking about structure, flow, dependencies
   (e.g. 'how do modules connect', 'what calls X', 'walk me through Y')

 Question: {question}

 Reply with only the category word."""

    try:
        current_client = next(client_cycle)
        response = current_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=MODEL_NAME,
            temperature=0.0,
        )

        result = response.choices[0].message.content.strip().lower()
        
        valid_categories = {"lookup", "explanation", "architectural"}
        if result not in valid_categories:
            logger.warning(
                f"Unexpected classifier response format: '{result}'. "
                "Defaulting to 'explanation'."
            )
            return "explanation"

        return result

    except Exception as e:
        logger.error(f"Error classifying query: {e}")
        return "explanation"
