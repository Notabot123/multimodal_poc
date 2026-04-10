## Mulitmodal poc

``` bash
cd backend
python -m venv venv
pip install -r requirements.txt
```

``` bash
cd backend
venv/Scripts/activate
uvicorn main:app --reload
```

for frontend..

```
cd frontend
npm install
npm run dev
```
## .env File
.env var:
```
OPENAI_API_KEY = your_key_here
GEMINI_API_KEY=your_key_here
EMBEDDING_MODE=openai
LOAD_PREBUILT_DB=true
```

EMBEDDING_MODE - can be set as openai, gemini or mock (or left blank defaults mock)

LOAD_PREBUILT_DB just contains a few samples.
You'd want to copy 'samples' to 'uploads' folder, if you're on a device without access to openAI/other

## Database reset
to reset db:
```
rm db.json
rm faiss.index
rm -rf uploads/
```