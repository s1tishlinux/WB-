import weave
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import time

@weave.op()
class MemoryManager:
    """Memory management with semantic search capabilities"""
    
    def __init__(self, memory_file: str = "agent_memory.json", max_memories: int = 1000):
        self.memory_file = memory_file
        self.max_memories = max_memories
        self.memories = []
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.load_memory()
    
    def load_memory(self):
        """Load existing memories from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memories = json.load(f)
            except:
                self.memories = []
    
    def save_memory(self):
        """Save memories to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories[-self.max_memories:], f, indent=2)
    
    @weave.op()
    def add_interaction(self, content: str, role: str):
        """Add new interaction to memory"""
        memory_entry = {
            "content": content,
            "role": role,
            "timestamp": time.time()
        }
        self.memories.append(memory_entry)
        
        # Keep only recent memories
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
        
        self.save_memory()
    
    @weave.op()
    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant context using semantic search"""
        if not self.memories:
            return ""
        
        # Extract content for vectorization
        memory_texts = [m["content"] for m in self.memories]
        
        if len(memory_texts) < 2:
            return memory_texts[0] if memory_texts else ""
        
        try:
            # Vectorize memories and query
            all_texts = memory_texts + [query]
            vectors = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity
            query_vector = vectors[-1]
            memory_vectors = vectors[:-1]
            similarities = cosine_similarity(query_vector, memory_vectors).flatten()
            
            # Get top-k most similar memories
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            relevant_memories = [self.memories[i] for i in top_indices if similarities[i] > 0.1]
            
            # Format context
            context_parts = []
            for memory in relevant_memories:
                context_parts.append(f"{memory['role']}: {memory['content']}")
            
            return "\n".join(context_parts)
        
        except Exception as e:
            # Fallback to recent memories
            recent_memories = self.memories[-top_k:]
            return "\n".join([f"{m['role']}: {m['content']}" for m in recent_memories])
    
    @weave.op()
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.memories),
            "user_messages": len([m for m in self.memories if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.memories if m["role"] == "assistant"]),
            "memory_file": self.memory_file
        }