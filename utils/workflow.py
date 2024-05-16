from utils.corrective_elements import get_retriever,evaluator,rewriter,generic_rag
from utils.tools import search_web
from langchain.schema import Document

def retrieval_node(state):
    
    print("---RETRIEVAL---")
    print(state,"THIS IS THE STATE¡¡¡¡¡")
    
    question=state["question"]
    pdf=state["pdf"]
    retriever=get_retriever(pdf=pdf,k=3,chunk_size=1000,chunk_overlap=100)
    top_docs=retriever.invoke(question)
    
    return {"documents":top_docs,"question":question}
    
def grade_documents_node(state):
    print("---GRADING DOCUMENTS---")
    print(state,"THIS IS THE STATE IN GRADIENTS¡¡¡¡¡")
    question=state["question"]
    docs=state["documents"]
    ## filter
    filter_docs=[]
    web_search="no"
    relevant_docs=0

    for d in docs:
        grade=evaluator(question=question,doc=d.page_content)
        print(grade)
        if grade["grade"] == "yes":
            print("MATCH RELEVANT DOCUMENT")
            relevant_docs+=1
            filter_docs.append(d)
        else:
            print("MATCH IRRELEVANT DOCUMENT")
            continue
        if relevant_docs == 0:
            web_search="yes"

    print(filter_docs,"THIS ARE THE FILTER DOCS¡¡¡¡")
    return {"documents":filter_docs,"question":question,"web_search":web_search}
    
def decide_generate_node(state):
    print("---EVALUATE GENERATING---")
    web_search=state["web_search"]
    if web_search=="yes":
        ## returning flag to searching the web
        print("SEARCHING THE WEB...")
        return "searching" 
    else:
        ## returning flag to generate
        print("GENERATING RESPONSE...")
        return "generate"
    
def transform_query_node(state):
    print("--IMPROVING QUESTION--")
    question=state["question"]
    docs=state["documents"]
    update_question=rewriter(question=question)
    print(update_question,"THIS IS THE UPDATE QUESTION¡¡¡¡")
    return {"documents":docs,"question":update_question}

def web_search_node(state):
    print("---WEB SEARCHING---")
    query=state["question"]
    documents=state["documents"]
    results=search_web(k=5,query=query)
    update_docs="\n".join(doc["content"] for doc in results)
    update_docs=Document(page_content=update_docs)
    documents.append(update_docs)
    print(documents,"THIS ARE THE WEB SEARCH DOCUMENTS¡¡¡")
    return {"documents":documents,"question":query}

def generate_node(state):
    print("--- GENERATING RESPONSE---")
    docs=state["documents"]
    query=state["question"]
    response=generic_rag(docs=docs,question=query)
    return {"document":docs,"question":query,"generate":response}