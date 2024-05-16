
from typing_extensions import TypedDict
from typing import List
from langgraph.graph import END,StateGraph
from utils.workflow import retrieval_node,grade_documents_node,decide_generate_node,web_search_node,transform_query_node,generate_node 
from pprint import pprint
import re
from utils.models import CorrectiveItems

class CorrectiveRAG(TypedDict):
    question:str
    generate:str
    web_search:str
    documents:List[str]
    pdf:str
    
workflow=StateGraph(CorrectiveRAG)

#TODO define nodes
workflow.add_node("retrieval",retrieval_node)
workflow.add_node("evaluator",grade_documents_node)
workflow.add_node("rewriter",transform_query_node)
workflow.add_node("searcher",web_search_node)
workflow.add_node("generator",generate_node)

#TODO define edges 
workflow.set_entry_point("retrieval")
workflow.add_edge("retrieval","evaluator")
workflow.add_conditional_edges("evaluator",
                               decide_generate_node,
                               {"searching":"rewriter","generate":"generator"})
workflow.add_edge("rewriter","searcher")
workflow.add_edge("searcher","generator")
workflow.add_edge("generator",END)

#TODO graph compile
app =workflow.compile()


def corrective_app(path:str,question:str):
    pattern=re.compile(r'generator')
    response=""
    inputs={"pdf":path,"question":question}
    for output in app.stream(inputs):
        for key,value in output.items():
     # Node
            pprint(f"Node '{key}':")
            # Optional: print full state at each node
            # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
            if pattern.search(key):
              response=value["generate"]
            pprint("\n---\n")

    if response:
        return response
    else:
        return "Something went wrong...Try later"
        
