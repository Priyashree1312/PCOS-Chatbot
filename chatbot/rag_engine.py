# chatbot/rag_engine.py - FULLY FIXED VERSION (Copy-Paste Replace Entire File)
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from django.conf import settings
import logging
import time
import functools
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

# 🌸 PINKY PCOS HELPER - DISABLED "OOPS LOVELY!" FOREVER
PCOS_FAST_RESPONSES = {
    "symptoms": """💕 **PCOS Symptoms (Rotterdam criteria):** 
    - Irregular periods (oligoovulation) 
    - Excess hair (hirsutism), acne 
    - Weight gain around abdomen
    - Polycystic ovaries on ultrasound 🌸""",
    
    "diet": """🥗 **Indian PCOS Diet (NO maida!):**
    - **Breakfast:** Ragi porridge, sprouts, green tea
    - **Lunch:** Millet roti, dal, veggies, curd
    - **Dinner:** Grilled fish/chicken, salad
    - **Avoid:** Sweets, maida, fried foods 💚""",
    
    "treatment": """⚕️ **PCOS Treatments:**
    - **Lifestyle:** 5-10% weight loss = 50% symptom improvement!
    - **Meds:** Metformin (insulin), OCPs (hormones)
    - **Supplements:** Inositol, Vitamin D 🩺""",
    
    "yoga": """🧘‍♀️ **Best Yoga Poses (15 mins daily):**
    - Butterfly Pose (Baddha Konasana) - ovaries
    - Cobra Pose (Bhujangasana) - hormones  
    - Bridge Pose (Setu Bandhasana) - thyroid 🌺""",
    
    "rotterdam": """📊 **Rotterdam Criteria (Diagnose PCOS):**
    Need **2 out of 3**:
    1. Irregular periods (<8/year or >35 days)
    2. High androgens (hirsutism/acne)
    3. Polycystic ovaries (12+ follicles) 🔬""",
    
    "medicine": """💊 **Common PCOS Medications:**
    - **Metformin** 500-2000mg (insulin resistance)
    - **OCPs** (hormone balance, acne)
    - **Spironolactone** (excess hair)
    **Doctor consultation required!** 📋"""
}

class PCOSFAISS:
    """🚀 500MB FAISS RAG - NO CRASHES"""
    def __init__(self, index_path="./faiss_pcos"):
        self.index_path = index_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.metadata = []
        self._load_index()
    
    def _load_index(self):
        if os.path.exists(f"{self.index_path}.faiss") and os.path.exists(f"{self.index_path}.pkl"):
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            with open(f"{self.index_path}.pkl", "rb") as f:
                data = pickle.load(f)
                self.documents = data['docs']
                self.metadata = data['meta']
            logger.info(f"✅ Loaded {len(self.documents)} PCOS docs")
        else:
            dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dim)
            logger.info("🆕 FAISS index created")
    
    def add_documents(self, documents: List[dict]):
        texts = [doc['content'] for doc in documents]
        embeddings = self.model.encode(texts, batch_size=4, show_progress_bar=False)
        self.index.add(embeddings.astype('float32'))
        self.documents.extend(texts)
        self.metadata.extend([doc['meta'] for doc in documents])
        self._save_index()
    
    def _save_index(self):
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        with open(f"{self.index_path}.pkl", "wb") as f:
            pickle.dump({'docs': self.documents, 'meta': self.metadata}, f)
    
    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        query_emb = self.model.encode([query])
        distances, indices = self.index.search(query_emb.astype('float32'), k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distances[0][i])))
        return results

class PCOSRAGEngine:
    def __init__(self):
        self.faiss = PCOSFAISS()
        self.llm = None
        self._cache = {}
        self._init_llm()
    
    def _init_llm(self):
        try:
            self.llm = ChatOllama(
                model="llama3.2:3b",
                base_url=getattr(settings, "OLLAMA_URL", "http://localhost:11434"),
                temperature=0.1,
                timeout=15
            )
        except Exception as e:
            logger.error(f"LLM init failed: {e}")
    
    def chat(self, question: str) -> str:
        """🚀 FIXED CHAT - Keywords → RAG → LLM (NO "oops lovely!")"""
        if not self.llm:
            return "⚠️ Start Ollama: ollama serve"
        
        question_lower = question.lower().strip()
        
        # 🌟 1. PINKY KEYWORDS FIRST (INSTANT RESPONSES)
        for keyword, response in PCOS_FAST_RESPONSES.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', question_lower, re.IGNORECASE):
                logger.info(f"✅ Pinky keyword match: {keyword}")
                return response
        
        # 2. GREETING RESPONSES
        greetings = ['hi', 'hello', 'hey', 'start', 'help', '']
        if question_lower in greetings or len(question.split()) <= 1:
            return "🌸 **Hi lovely! 💕** I'm Pinky, your PCOS bestie! Ask about: **symptoms**, **diet**, **treatment**, **yoga**, **medicine** ✨"
        
        # 3. MEMORY CACHE
        q_hash = hash(question_lower)
        if q_hash in self._cache:
            return self._cache[q_hash]
        
        # 4. FAISS RAG
        try:
            context = self._get_context(question)
            messages = [
                SystemMessage(content="PCOS expert. Simple answers for Indian women. Use context provided."),
                HumanMessage(content=f"Q: {question}\nContext: {context}")
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            self._cache[q_hash] = answer
            logger.info("✅ RAG response generated")
            return answer
            
        except Exception as e:
            logger.error(f"RAG failed: {e}")
            return "💕 Ask about **symptoms**, **diet**, **yoga**, or **treatment** for PCOS help! 🌸"
    
    @functools.lru_cache(maxsize=128)
    def _get_context(self, question_hash: str) -> str:
        """FAISS-powered context retrieval"""
        results = self.faiss.similarity_search(question_hash, k=2)
        return "\n".join([doc[0][:400] for doc in results])
    
    def build_db(self):
        """Build FAISS DB from your PDFs"""
        self._build_db()
        logger.info("✅ FAISS PCOS DB built!")
    
    def _build_db(self):
        """Safe PDF → FAISS pipeline"""
        data_path = "./data/"
        if not os.path.exists(data_path):
            default_docs = [
                {'content': 'PCOS Rotterdam criteria: 2/3 oligoovulation, hyperandrogenism, polycystic ovaries.', 'meta': 'rotterdam'},
                {'content': 'PCOS treatment: Lifestyle first, then metformin, COCs, ovulation induction.', 'meta': 'treatment'},
                {'content': 'Indian PCOS diet: Millets, low GI foods, no maida, healthy fats.', 'meta': 'diet'},
            ]
            self.faiss.add_documents(default_docs)
            return
        
        try:
            from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            loader = DirectoryLoader(data_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            splits = splitter.split_documents(docs)
            
            faiss_docs = [{'content': doc.page_content, 'meta': getattr(doc, 'metadata', {})} 
                         for doc in splits[:100]]
            self.faiss.add_documents(faiss_docs)
        except ImportError:
            logger.warning("Install: pip install pypdf langchain-community")

_rag_engine = None

def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = PCOSRAGEngine()
    return _rag_engine
