from fastapi import FastAPI, HTTPException, Query
from utils import get_pdf_links, download_pdfs, extract_text_from_pdfs
from summarizer import summarize_text
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    
)

@app.get("/")
def home():
    return {"message": "Welcome to the PDF Summarizer API!"}

@app.get("/Search/")
def summarize(query: str = Query(..., description="Google search query")):
    try:
        pdf_links = get_pdf_links(query)
        print(pdf_links)
        if not pdf_links:
            return {"error": "No PDFs found"}

        # download_pdfs(pdf_links)
        # extracted_text = extract_text_from_pdfs()

        # summary = summarize_text(extracted_text)
        return pdf_links

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
