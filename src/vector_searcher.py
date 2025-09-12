import os
import weaviate
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class VectorSearcher:
    def __init__(self):
        self.weaviate_url = os.getenv('WEAVIATE_URL')
        self.weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        if not all([self.weaviate_url, self.weaviate_api_key, self.google_api_key]):
            raise ValueError("Missing required environment variables: WEAVIATE_URL, WEAVIATE_API_KEY, GOOGLE_API_KEY")
        
        genai.configure(api_key=self.google_api_key)
        
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(self.weaviate_api_key)
        )
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for the user query"""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return []
    
    def search_cyberlaw(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search CyberLaw collection for relevant legal sections"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("CyberLaw")
            
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "section_number": item.properties.get('section_number', ''),
                    "title": item.properties.get('title', ''),
                    "content": item.properties.get('content', ''),
                    "law_type": item.properties.get('law_type', ''),
                    "summary": item.properties.get('summary', ''),
                    "full_text": item.properties.get('full_text', ''),
                    "source_file": item.properties.get('source_file', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"Error searching CyberLaw: {e}")
            return []
    
    def search_faq(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search FAQ collection for relevant questions and answers"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("FAQ")
            
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "question": item.properties.get('question', ''),
                    "answer": item.properties.get('answer', ''),
                    "category": item.properties.get('category', ''),
                    "source_file": item.properties.get('source_file', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"Error searching FAQ: {e}")
            return []
    
    def search_nodal_officers(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search NodalOfficer collection for relevant contact information"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("NodalOfficer")
            
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "state": item.properties.get('state', ''),
                    "officer_name": item.properties.get('officer_name', ''),
                    "rank": item.properties.get('rank', ''),
                    "email": item.properties.get('email', ''),
                    "contact": item.properties.get('contact', ''),
                    "source_file": item.properties.get('source_file', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"Error searching NodalOfficer: {e}")
            return []
    
    def comprehensive_search(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Search all collections and return comprehensive results"""
        return {
            "cyberlaw": self.search_cyberlaw(query, limit=15),  # Increased from 3 to 15
            "faq": self.search_faq(query, limit=8),  # Increased from 2 to 8
            "nodal_officers": self.search_nodal_officers(query, limit=8)
        }
    
    def close(self):
        """Close the Weaviate client connection"""
        if hasattr(self, 'client'):
            self.client.close()

if __name__ == "__main__":
    # Test the vector searcher
    searcher = VectorSearcher()
    
    test_query = "cyber crime FIR registration"
    print(f"Testing search for: {test_query}")
    
    results = searcher.comprehensive_search(test_query)
    
    print("\n=== CYBER LAW RESULTS ===")
    for result in results['cyberlaw']:
        print(f"Section {result['section_number']}: {result['title']} ({result['law_type']})")
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Distance: {result['distance']:.4f}")
        print("-" * 50)
    
    print("\n=== FAQ RESULTS ===")
    for result in results['faq']:
        print(f"Q: {result['question']}")
        print(f"A: {result['answer'][:100]}...")
        print(f"Distance: {result['distance']:.4f}")
        print("-" * 50)
    
    print("\n=== NODAL OFFICERS ===")
    for result in results['nodal_officers']:
        print(f"State: {result['state']}")
        print(f"Officer: {result['officer_name']} ({result['rank']})")
        print(f"Email: {result['email']}")
        print(f"Distance: {result['distance']:.4f}")
        print("-" * 50)
    
    searcher.close()