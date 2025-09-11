import json
import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.config import Configure
import google.generativeai as genai
from typing import List, Dict, Any

load_dotenv()

class VectorProcessor:
    def __init__(self):
        self.weaviate_url = os.getenv('WEAVIATE_URL')
        self.weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        genai.configure(api_key=self.google_api_key)
        
        self.client = weaviate.connect_to_wcs(
            cluster_url=self.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(self.weaviate_api_key)
        )
        
    def create_schema(self):
        try:
            if self.client.collections.exists("CyberLaw"):
                self.client.collections.delete("CyberLaw")
            if self.client.collections.exists("FAQ"):
                self.client.collections.delete("FAQ")
            if self.client.collections.exists("NodalOfficer"):
                self.client.collections.delete("NodalOfficer")
            
            self.client.collections.create(
                name="CyberLaw",
                properties=[
                    weaviate.classes.config.Property(name="section_number", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="title", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="law_type", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="summary", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="full_text", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="source_file", data_type=weaviate.classes.config.DataType.TEXT)
                ]
            )
            
            self.client.collections.create(
                name="FAQ",
                properties=[
                    weaviate.classes.config.Property(name="question", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="answer", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="category", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="source_file", data_type=weaviate.classes.config.DataType.TEXT)
                ]
            )
            
            self.client.collections.create(
                name="NodalOfficer",
                properties=[
                    weaviate.classes.config.Property(name="state", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="officer_name", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="rank", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="email", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="contact", data_type=weaviate.classes.config.DataType.TEXT),
                    weaviate.classes.config.Property(name="source_file", data_type=weaviate.classes.config.DataType.TEXT)
                ]
            )
            
            print("Schema created successfully!")
        except Exception as e:
            print(f"Error creating schema: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def process_bns_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        objects = []
        for section in data['bns_sections']:
            content = f"Section {section['section_number']}: {section['title']}\n{section['summary']}"
            full_text = json.dumps(section['full_legal_text'])
            
            embedding = self.generate_embedding(content)
            
            objects.append({
                "properties": {
                    "section_number": section['section_number'],
                    "title": section['title'],
                    "content": content,
                    "law_type": "BNS",
                    "summary": section['summary'],
                    "full_text": full_text,
                    "source_file": "bns.json"
                },
                "vector": embedding
            })
        
        return objects
    
    def process_ipc_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        objects = []
        for section in data['ipc_sections']:
            content = f"Section {section['section_number']}: {section['title']}\n{section['plain_english']}"
            
            full_text = section['official_text']
            if isinstance(full_text, dict):
                full_text = json.dumps(full_text)
            
            embedding = self.generate_embedding(content)
            
            objects.append({
                "properties": {
                    "section_number": section['section_number'],
                    "title": section['title'],
                    "content": content,
                    "law_type": "IPC",
                    "summary": section['plain_english'],
                    "full_text": str(full_text),
                    "source_file": "ipc.json"
                },
                "vector": embedding
            })
        
        return objects
    
    def process_it_act_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        objects = []
        for section in data['it_act_sections']:
            content = f"Section {section['section_number']}: {section['title']}\n{section['summary']}"
            full_text = json.dumps(section['full_legal_text'])
            
            embedding = self.generate_embedding(content)
            
            objects.append({
                "properties": {
                    "section_number": section['section_number'],
                    "title": section['title'],
                    "content": content,
                    "law_type": "IT_ACT",
                    "summary": section['summary'],
                    "full_text": full_text,
                    "source_file": "it.json"
                },
                "vector": embedding
            })
        
        return objects
    
    def process_faq_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        objects = []
        
        if isinstance(data, list):
            faq_list = data
        elif isinstance(data, dict) and 'faqs' in data:
            faq_list = data['faqs']
        else:
            print(f"Unknown FAQ format in {file_path}")
            return objects
        
        for item in faq_list:
            content = f"Q: {item['question']}\nA: {item['answer']}"
            
            embedding = self.generate_embedding(content)
            
            objects.append({
                "properties": {
                    "question": item['question'],
                    "answer": item['answer'],
                    "category": "cybercrime_faq",
                    "source_file": os.path.basename(file_path)
                },
                "vector": embedding
            })
        
        return objects
    
    def process_nodal_officers_data(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        objects = []
        for officer in data:
            content = f"State: {officer['state_ut']}\nNodal Officer: {officer['nodal_officer']['name']}, {officer['nodal_officer']['rank']}\nEmail: {officer['nodal_officer']['email']}"
            
            embedding = self.generate_embedding(content)
            
            objects.append({
                "properties": {
                    "state": officer['state_ut'],
                    "officer_name": officer['nodal_officer']['name'],
                    "rank": officer['nodal_officer']['rank'],
                    "email": officer['nodal_officer']['email'],
                    "contact": officer.get('grievance_officer', {}).get('contact', ''),
                    "source_file": "nodal_officers.json"
                },
                "vector": embedding
            })
        
        return objects
    
    def batch_upload(self, collection_name: str, objects: List[Dict]):
        try:
            collection = self.client.collections.get(collection_name)
            
            data_objects = []
            for obj in objects:
                data_objects.append(
                    weaviate.classes.data.DataObject(
                        properties=obj["properties"],
                        vector=obj["vector"]
                    )
                )
            
            collection.data.insert_many(data_objects)
            print(f"Successfully uploaded {len(objects)} objects to {collection_name}")
        except Exception as e:
            print(f"Error uploading objects to {collection_name}: {e}")
    
    def process_all_files(self):
        knowledge_base_path = "Knowledge_base"
        
        law_processors = {
            "bns.json": self.process_bns_data,
            "ipc.json": self.process_ipc_data,
            "it.json": self.process_it_act_data,
        }
        
        faq_processors = {
            "cybercrime_faq_dynamic.json": self.process_faq_data,
            "faq.json": self.process_faq_data,
        }
        
        officer_processors = {
            "nodal_officers.json": self.process_nodal_officers_data
        }
        
        for filename, processor in law_processors.items():
            file_path = os.path.join(knowledge_base_path, filename)
            if os.path.exists(file_path):
                print(f"Processing {filename}...")
                objects = processor(file_path)
                self.batch_upload("CyberLaw", objects)
            else:
                print(f"File {filename} not found")
        
        for filename, processor in faq_processors.items():
            file_path = os.path.join(knowledge_base_path, filename)
            if os.path.exists(file_path):
                print(f"Processing {filename}...")
                objects = processor(file_path)
                self.batch_upload("FAQ", objects)
            else:
                print(f"File {filename} not found")
        
        for filename, processor in officer_processors.items():
            file_path = os.path.join(knowledge_base_path, filename)
            if os.path.exists(file_path):
                print(f"Processing {filename}...")
                objects = processor(file_path)
                self.batch_upload("NodalOfficer", objects)
            else:
                print(f"File {filename} not found")

if __name__ == "__main__":
    processor = VectorProcessor()
    processor.create_schema()
    processor.process_all_files()
    print("Vector processing completed!")
    processor.client.close()
