import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import chromadb

class RAGComparator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"--- Initializing Embedding Model: {model_name} ---")
        self.model = SentenceTransformer(model_name)
        self.chroma_client = chromadb.Client()

    def process_pdf(self, path, size=600):
        """Extracts text from PDF and splits into fixed-size chunks."""
        reader = PdfReader(path)
        text = "".join([p.extract_text() or "" for p in reader.pages])
        return [text[i:i+size] for i in range(0, len(text), size)]

    def process_txt(self, path):
        """Extracts text from TXT and splits by paragraphs."""
        with open(path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        return [c.strip() for c in raw_text.split('\n\n') if len(c.strip()) > 20]

    def run_benchmark(self, chunks, query):
        # 1. Generate Embeddings
        print(f"🧠 Encoding {len(chunks)} chunks...")
        chunk_embeddings = self.model.encode(chunks)
        query_vec = self.model.encode([query])

        # --- Method A: NumPy (Vector-DB-less) ---
        t0 = time.time()
        scores = cosine_similarity(query_vec, chunk_embeddings).flatten()
        best_idx_numpy = np.argmax(scores)
        numpy_time = (time.time() - t0) * 1000

        # --- Method B: ChromaDB (Traditional) ---
        t1 = time.time()
        # Create a unique collection for this run
        collection = self.chroma_client.create_collection(name=f"compare_{int(time.time())}")
        collection.add(
            ids=[str(i) for i in range(len(chunks))],
            embeddings=chunk_embeddings.tolist(),
            documents=chunks
        )
        results = collection.query(query_embeddings=query_vec.tolist(), n_results=1)
        chroma_time = (time.time() - t1) * 1000

        return {
            "numpy_time": numpy_time,
            "chroma_time": chroma_time,
            "best_text": chunks[best_idx_numpy],
            "num_chunks": len(chunks)
        }

    def visualize_results(self, metrics):
        plt.figure(figsize=(8, 5))
        methods = ['NumPy (DB-less)', 'ChromaDB']
        times = [metrics['numpy_time'], metrics['chroma_time']]
        
        plt.bar(methods, times, color=['#4CAF50', '#2196F3'])
        plt.ylabel('Latency (ms)')
        plt.title(f'RAG Speed Comparison ({metrics["num_chunks"]} Chunks)')
        plt.show()

def main():
    comparator = RAGComparator()
    
    # File Selection Logic
    file_path = input("Enter the path to your PDF or TXT file: ").strip()
    
    if not os.path.exists(file_path):
        print("File not found!")
        return

    if file_path.endswith('.pdf'):
        chunks = comparator.process_pdf(file_path)
    else:
        chunks = comparator.process_txt(file_path)

    print(f"✅ Success! Processed {len(chunks)} chunks.")
    query = input("\n🔍 Enter your search query: ")

    results = comparator.run_benchmark(chunks, query)
    
    # Display Results
    print("\n" + "="*40)
    print("📊 PERFORMANCE BENCHMARK")
    print("="*40)
    print(f"NumPy Latency:    {results['numpy_time']:.4f} ms")
    print(f"ChromaDB Latency: {results['chroma_time']:.4f} ms")
    print(f"\n⚡ RESULT: NumPy was {results['chroma_time']/results['numpy_time']:.1f}x faster for this scale.")
    print(f"\n🎯 TOP MATCH:\n\"{results['best_text'][:250]}...\"")

    comparator.visualize_results(results)

if __name__ == "__main__":
    main()