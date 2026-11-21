import sys

from retrieval import retriever, vector_store

question = " ".join(sys.argv[1:]) or "Who can register a business name with DTI?"

found = vector_store.similarity_search_with_score(question, k=5)
picked = retriever.invoke(question)

print(f"Question: {question}")
print(f"Closest distance: {found[0][1]:.3f}")
print("\nTop 5 by meaning:")
for doc, distance in found:
    print(f"  {doc.metadata['id']}  {distance:.3f}  {doc.metadata['title']}")
print("\nRetriever picks:")
for doc in picked:
    print(f"  {doc.metadata['id']}  {doc.metadata['title']}")