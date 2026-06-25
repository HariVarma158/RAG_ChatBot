from fastapi import FastAPI, File, UploadFile as UF, Query
from pypdf import PdfReader
from src.config import chromaDb as chdb

def load_pdf(file: UF):
    txt=""
    reader=PdfReader(file.file)
    for page in reader.pages:
        text1=page.extract_text()
        if text1:
            txt+=text1
    return txt

def chunk_text(text:str):
    chunks=chdb.text_splitter.split_text(text)
    return chunks

def chroma_ingest(file:UF,chunks):
    documents,metadatas,ids=[],[],[]
    for idx,chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append(
            {
                "source":file.filename
            }
        )
        ids.append(f"{file.filename}_chunk_{idx}")
        chdb.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    print("*"*50)
    print(f"File Ingestion done")