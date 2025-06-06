from fastapi import FastAPI
from pydantic import BaseModel
import openai
from openai import OpenAI
import os
import traceback
from fastapi.responses import JSONResponse
from fastapi import Request

app = FastAPI()
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 Exception caught in global handler:")
    print(traceback.format_exc())
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

if os.getenv("OPEN_API_KEY"):
    API_KEY = os.getenv("OPEN_API_KEY")
else:
    print('No API KEY')
client = OpenAI(api_key=API_KEY)


class WordPairsRequest(BaseModel):
    selected_words: list
    customization: str

class GetQuotes(BaseModel):
    eng_words: list

class VersionCheckRequest(BaseModel):
    current_version: str
    platform: str  # or "mac", "linux"

class UpdateInfoResponse(BaseModel):
    update_available: bool
    latest_version: str
    download_url: str
    size: int
    release_notes: str
    mandatory: bool

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
    print(completion)

    return {"result": completion.choices[0].message.content}

@app.post("/get_quotes")
async def get_word_pairs_endpoint(req: GetQuotes):
    prompt = f"For each of the words in {req.eng_words} give me a motivational or iconic quotes or popular saying that includes the word or the closest relation, with author and year. Format: Quote — Author (Year). If it is a popular saying, use '*language of origin saying' as author. No quotes, no numbering, no bullet points."
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    print(completion)

    return {"result": completion.choices[0].message.content}
    

@app.post("/check_update")
async def check_update_endpoint(req: VersionCheckRequest):
    # This would typically come from your database or version control system
    LATEST_VERSION = "2.0.1"
    RELEASE_NOTES = "Testing Updates"
    
    # Platform-specific download URLs
    DOWNLOAD_URLS = {
        "windows": "https://github.com/devz999/Murmur_UI/raw/main/Murmur_v2.0.1.zip",
        "mac": "https://github.com/devz999/Murmur_UI/raw/main/Murmur_v2.0.1.zip",
        "linux": "https://github.com/devz999/Murmur_UI/raw/main/Murmur_v2.0.1.zipp"
    }
    
    # Compare versions (simple string comparison - for semantic versioning you'd need more logic)
    if req.current_version < LATEST_VERSION:
        return UpdateInfoResponse(
            update_available=True,
            latest_version=LATEST_VERSION,
            download_url=DOWNLOAD_URLS.get(req.platform, DOWNLOAD_URLS["windows"]),
            size=8928256,
            release_notes=RELEASE_NOTES,
            mandatory=is_mandatory_update(req.current_version))
    else:
        return UpdateInfoResponse(
            update_available=False,
            latest_version=req.current_version,
            download_url="",
            size=0,
            release_notes=""
        )

def get_remote_file_size(url: str) -> int:
    """Helper function to get remote file size without downloading"""
    try:
        response = requests.head(url, allow_redirects=True)
        return int(response.headers.get('content-length', 0))
    except:
        return 1

def is_mandatory_update(current_version: str) -> bool:
    """Determine if this is a mandatory update (e.g., security fixes)"""
    # Implement your logic here - this is just an example
    MANDATORY_MIN_VERSION = "2.0.1"
    print(current_version, MANDATORY_MIN_VERSION)
    return current_version < MANDATORY_MIN_VERSION
