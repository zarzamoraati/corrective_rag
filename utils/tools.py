from langchain_community.tools.tavily_search import TavilySearchResults

def search_web(k:int,query:str):
    search_tool=TavilySearchResults(k=k)
    return search_tool.invoke({"query":query})