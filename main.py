from corrective_rag import corrective_app
from fastapi import FastAPI,UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import os

#TODO implementing  API


app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=["*"],
    allow_credentials=True,
)

@app.post("/api/generate")
async def request_generate(pdf:UploadFile,question:Annotated[str,Form()]):
    try:
        if not pdf or not question:
            raise ValueError("The request is not valid. Fields shouldn't be empty")
        else:
            ##TODO process PDF path
            content_pdf= await pdf.read()
            current_dir = os.getcwd()
            path_pdf=os.path.join(current_dir,"test.pdf")
            with open(path_pdf,"wb") as f:
                f.write(content_pdf)
                
            if os.path.exists(path_pdf):
                response=corrective_app(path_pdf,question)
                return response
            else:
                raise ValueError("The path is not valid or something went wrong during the lecture of the content")

    except ValueError as e:
        return e.args[0]
        

@app.get("/")
def home_page():
    return "Hellow World"


