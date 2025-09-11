import os
from dotenv import load_dotenv
import weaviate
import google.generativeai as genai

load_dotenv()

def test_vector_search():
    client = weaviate.connect_to_wcs(
        cluster_url=os.getenv('WEAVIATE_URL'),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_API_KEY'))
    )
    
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    query = "How to report cybercrime online?"
    
    query_embedding = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query"
    )['embedding']
    
    collection = client.collections.get("FAQ")
    response = collection.query.near_vector(
        near_vector=query_embedding,
        limit=3
    )
    
    print(f"Query: {query}")
    print("\nTop Results:")
    for i, item in enumerate(response.objects, 1):
        print(f"\n{i}. {item.properties['question']}")
        print(f"   Answer: {item.properties['answer'][:200]}...")
    
    client.close()

if __name__ == "__main__":
    test_vector_search()
