from fastapi import FastAPI
from pydantic import BaseModel
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
if os.getenv("OPEN_API_KEY"):
    API_KEY = os.getenv("OPEN_API_KEY")
else:
    print('No API KEY')
client = OpenAI(api_key=API_KEY)
app = FastAPI()

class WordPairsRequest(BaseModel):
    selected_words: list
    customization: str

@app.get("/")
async def root():
    return {"message": "Server is alive, Dev!"}

@app.post("/get_word_pairs")
async def get_word_pairs_endpoint(req: WordPairsRequest):
    word_prompt = (
        f"Out of the following 20 words, where each entry in the list is [language,[words]], pick exactly 10 that are the most commonly used or easiest to learn. "
        f"Return them in this format: A list of lists where each sublist is strictly: [Word in foreign language, English translation,emoji for language,Sample sentence in language,US emoji, English translation of that sentence], dont need captions, just the element, neatly in a list. I DO NOT want the name of language anywhere, except for emoji, i want just one single list of 10 sublists as output. "
        f"Generated 10 sentences should be relevant to the following context or scenarios: {req.customization} Return in this exact list form, just 6 entries per sublist.\n\n"
        + str(req.selected_words)
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": word_prompt}]
    )

    return {"result": completion.choices[0].message.content}
