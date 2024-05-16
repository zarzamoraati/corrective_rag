import os
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from fastapi import UploadFile 
load_dotenv()


#TODO retriever

def get_retriever(pdf:UploadFile,k:int,chunk_size:int,chunk_overlap:int) -> VectorStoreRetriever:
    loader=PyPDFLoader(pdf)
    docs=loader.load()
    splitter=RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    chunks=splitter.split_documents(docs)
    embeddings=GPT4AllEmbeddings()
    vectordb=Chroma.from_documents(chunks,embedding=embeddings)
    retriever=vectordb.as_retriever(k=k)
    return retriever

#TODO Evaluator

def evaluator(doc:str,question):
    prompt=PromptTemplate(
        # template="""
        # You're a grader assesing relevance of a retriever document to a user question.\n
        # First evalute the subject of the retriever document searching for keywords and determinate if is related to the user question.\n
        # If the document doesn't contain any keyworkd related to the user question evaluate it as no relevant , if contain one or more keyword evalute it as relevant.\n
        # Here is the retriever document:{context}\n
        # Here is the user question: {question}\n
        # - VERY IMPORTANT: Your response must limitate to a JSON Object with a key 'grade' and its value 'yes' or 'not',
        # """"",
        template=""""Evalute the content of the context and search for keywords. If the context contain one or more keywords garde it as relevant otherwise grade it as irrelevant.\n
        -This is the context :{context}\n
        -This is the question: {question}\n
        
        Important :  RESPOND WITH A JSON OBJECT either if the context is relevant or not. Nothing else- The JSON object must contain only a key 'grade' and its value 'yes' or 'not'. """,
        input_variables=["question","context"]
    )
    llm=ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.1)
    
    evaluator_chain=prompt|llm|JsonOutputParser()
    return evaluator_chain.invoke({"question":question,"context":doc})

#TODO REWRITER

def rewriter(question):
    prompt=PromptTemplate(
        template="""You're a question re-writer taht converts an input question to a better version that is optimized for vectorstore retrieval.\n
          Here is the input question : {question}.
          
          -IMPORTANT: RESPOND WITH THE UPADTE QUESTION ONLY, NOTHING ELSE.""",
        input_variables=["question"]
    )
    llm=ChatGroq(model="Llama3-8b-8192",temperature=0.1)
    rewriter_chain=prompt|llm|StrOutputParser()    
    return rewriter_chain.invoke(question)

#TODO RAG

def generic_rag(docs,question):
    prompt=hub.pull("rlm/rag-prompt")   
    llm=ChatGroq(model="Llama3-8b-8192",temperature=0.2)
    rag_chain=prompt|llm|StrOutputParser()
    return rag_chain.invoke({"context":docs,"question":question})
    
