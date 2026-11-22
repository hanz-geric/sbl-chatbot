from langchain.tools import tool

from generator import clean_context
from retrieval import retriever


@tool(response_format="content_and_artifact", return_direct=True)
def search_knowledge_base(query: str):
    """
        Search the knowledge base for small business and livelihood information
        in Baguio City and Benguet: DTI business name registration, 
        business permits, BIR, barangay clearance, loans, grants, livelihood programs, 
        trainings and Negosyo Centers. Pass the user's question as the query, 
        word for word.
    """
    docs = retriever.invoke(query)
    context = "\n\n".join("### " + clean_context(doc.page_content) for doc in docs)

    return context, docs
