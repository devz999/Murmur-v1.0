from fastapi import FastAPI, Depends
from pydantic import BaseModel
import openai
from openai import OpenAI
import os
import traceback
from fastapi.responses import JSONResponse
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db, Base, engine
from models import UserPing
from datetime import datetime
import random
from git_write import update_github_file, generate_random_key_git, get_existing_keys_git,generate_unique_key_git

repo_owner_git="devz999"
repo_name_git="Murmur-v1.0"
file_path_git="murmurDB.csv"

#Devshan Fernando,2025
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

if os.getenv("GIT_REPO_KEY"):
    GIT_KEY = os.getenv("GIT_REPO_KEY")
else:
    print('No GIT_REPO_KEY')


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

class VerifyRequest(BaseModel):
    user: str
    timestamp: datetime
    location: dict
    languages: str
    custom: str

class VerifyResponse(BaseModel):
    user_key: str

@app.on_event("startup")
async def on_startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created.")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

async def generate_unique_key(db: AsyncSession) -> str:
    charset = string.ascii_uppercase + string.digits  # A-Z and 0-9
    for _ in range(10):
        key = ''.join(random.choices(charset, k=8))
        exists = await db.execute(select(UserPing).where(UserPing.user == key))
        if not exists.scalar():
            return key
    raise Exception("Ran out of unique keys. Congrats, you broke the universe.")

@app.post("/verify", response_model=VerifyResponse)
async def verify_user(req: VerifyRequest):
    user = req.user
    if user == "NA":
        user = generate_unique_key_git("https://raw.githubusercontent.com/devz999/Murmur-v1.0/main/murmurDB.csv")
        '''user = await generate_unique_key(db)

    user_data = await db.get(UserPing, user)
    if not user_data:
        user_data = UserPing(
            user=user,
            timestamp=req.timestamp,
            location=req.location
        )
        db.add(user_data)'''
    '''else:
        user_data.timestamp = req.timestamp
        user_data.location = req.location'''

    #await db.commit()
    loc = req.location
    data_git=f"{user},{req.timestamp.isoformat()},{loc.get('city','')},{loc.get('region','')},{loc.get('country','')},{req.languages},{req.custom}\n"
    update_github_file(GIT_KEY,repo_owner_git,repo_name_git,file_path_git,data_git,"Update file via API","Dev","dev@example.com")
    return {"user_key": user}
