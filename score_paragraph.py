# implements relevance scoring for paragraphs with reference text -> replace paragraphs (under main) with actual paragraphs

import pandas as pd
import hashlib
import requests
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    response.raise_for_status()
    with open("reference_text.pdf", "wb") as file:
        file.write(response.content)
    reader = PdfReader("reference_text.pdf")
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def calculate_relevance(paragraph: str, reference_text: str) -> float:
    reference_embedding = model.encode(reference_text, convert_to_tensor=True)
    paragraph_embedding = model.encode(paragraph, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(paragraph_embedding, reference_embedding).item()
    log_score = np.log1p(similarity + 1e-10)
    return log_score * 10

def score_paragraphs(paragraphs, reference_text):
    scored_data = []
    for paragraph in paragraphs:
        relevance = calculate_relevance(paragraph, reference_text)
        paragraph_id = hashlib.md5(paragraph.encode()).hexdigest()[:8]
        scored_data.append({
            "id": paragraph_id,
            "paragraph": paragraph,
            "score": relevance
        })
    return pd.DataFrame(scored_data)

if __name__ == "__main__":
    pdf_url = "https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/11/responsible-business-conduct-for-climate-action_b9b43c9c/d098b352-en.pdf"
    reference_text = extract_text_from_pdf(pdf_url)
    
    paragraphs = [
        "Investing in renewable energy sources such as solar and wind can significantly reduce a company's carbon footprint.",
        "Reducing emissions is important for sustainability.",
        "Companies should consider regulatory compliance to avoid fines and penalties in the future.",
        "Advancing carbon capture technology could be a game changer in industrial sustainability.",
        "Water conservation strategies should be considered for long-term environmental responsibility."
    ]
    
    df = score_paragraphs(paragraphs, reference_text)
    
    df.to_csv("scored_paragraphs.csv", index=False)
    
    print(df)