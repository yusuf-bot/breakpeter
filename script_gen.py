
import os
from dotenv import load_dotenv
load_dotenv()
import requests

from news import get_latest_headlines_and_summaries

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-medium" 


def generate_script_with_mistral(title, content):
    SYSTEM_PROMPT = "You are a scriptwriter for a viral Instagram account. Your job is to write funny Minecraft conversations between Peter Griffin and Stewie from Family Guy."

    USER_PROMPT = f"""
        Write a short, funny, conversational exchange between Stewie and Peter Griffin from Family Guy. 
        Stewie is asking Peter about this news headline and Peter is trying to explain what happened using information from the article.
        Stewie should not refer or quote the headline directly, but should ask questions that relate to the content of the article.
        Headline: "{title}"
        Context: "{content}"

        Stewie should ask 1-2 sarcastic, curious follow-up questions. 
        Peter should respond with casual, exaggerated, or comedic explanations that reflect the actual content.
        Keep the tone light and funny, but make sure the conversation includes the key information from the context.

        Format:
        Stewie: ...
        Peter: ...

        """

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]

    data = {
        "model": MISTRAL_MODEL,
        "messages": messages
    }

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        json=data,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"❌ Mistral API error {response.status_code}: {response.text}")
    
if __name__ == "__main__":
    articles = get_latest_headlines_and_summaries()
    print(generate_script_with_mistral(articles[0][0], articles[0][1]))