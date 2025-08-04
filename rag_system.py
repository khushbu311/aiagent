import chromadb
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Dict, Any
import os

class MenuRAG:
    def __init__(self, menu_items: List[Dict[str, Any]], persist_directory: str = "./data/menu_embeddings"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings()
        self.menu_items = menu_items
        self.vectorstore = None
        self.setup_rag()
    
    def setup_rag(self):
        """Setup RAG system with menu data"""
        # Create documents from menu items
        documents = []
        for item in self.menu_items:
            content = f"""
            Name: {item['name']}
            Category: {item['category']}
            Price: ${item['price']:.2f}
            Description: {item['description']}
            Available: {'Yes' if item['available'] else 'No'}
            """
            doc = Document(
                page_content=content,
                metadata={
                    'name': item['name'],
                    'category': item['category'],
                    'price': item['price'],
                    'id': item['id']
                }
            )
            documents.append(doc)
        
        # Create vector store
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def search_menu(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search menu items using RAG"""
        if not self.vectorstore:
            return []
        
        # Perform similarity search
        docs = self.vectorstore.similarity_search(query, k=k)
        
        results = []
        for doc in docs:
            results.append({
                'name': doc.metadata['name'],
                'category': doc.metadata['category'],
                'price': doc.metadata['price'],
                'content': doc.page_content,
                'id': doc.metadata['id']
            })
        
        return results
    
    def get_menu_context(self, query: str) -> str:
        """Get relevant menu context for the query"""
        search_results = self.search_menu(query)
        context = "Available menu items related to your query:\n\n"
        
        for item in search_results:
            context += f"- {item['name']} (${item['price']:.2f}) - {item['category']}\n"
        
        return context
