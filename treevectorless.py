import time
import numpy as np
from sklearn.neighbors import BallTree
from sklearn.preprocessing import normalize
# ... (keep your other imports)

class RAGComparator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"--- Initializing Embedding Model: {model_name} ---")
        self.model = SentenceTransformer(model_name)
        self.chroma_client = chromadb.Client()

    # ... (keep process_pdf and process_txt as they were)

    def run_benchmark(self, chunks, query):
        print(f"🧠 Encoding {len(chunks)} chunks...")
        chunk_embeddings = self.model.encode(chunks)
        query_vec = self.model.encode([query])

        # IMPORTANT: BallTree uses Euclidean distance by default.
        # To make it equivalent to Cosine Similarity, we NORMALIZE the vectors first.
        norm_chunks = normalize(chunk_embeddings)
        norm_query = normalize(query_vec)

        # --- Method A: NumPy (Brute Force) ---
        t0 = time.time()
        scores = cosine_similarity(query_vec, chunk_embeddings).flatten()
        best_idx_numpy = np.argmax(scores)
        numpy_time = (time.time() - t0) * 1000

        # --- Method B: BallTree (Search Index) ---
        # Note: Index building time is usually counted separately in production, 
        # but we'll include it or time just the query depending on your preference.
        t_build = time.time()
        tree = BallTree(norm_chunks, leaf_size=40) 
        build_time = (time.time() - t_build) * 1000
        
        t_query = time.time()
        dist, ind = tree.query(norm_query, k=1)
        balltree_time = (time.time() - t_query) * 1000

        # --- Method C: ChromaDB ---
        t1 = time.time()
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
            "balltree_time": balltree_time,
            "balltree_build": build_time,
            "chroma_time": chroma_time,
            "best_text": chunks[ind[0][0]],
            "num_chunks": len(chunks)
        }

    def visualize_results(self, metrics):
        plt.figure(figsize=(10, 6))
        methods = ['NumPy (Brute)', 'BallTree (Index)', 'ChromaDB']
        times = [metrics['numpy_time'], metrics['balltree_time'], metrics['chroma_time']]
        
        bars = plt.bar(methods, times, color=['#4CAF50', '#FF9800', '#2196F3'])
        plt.ylabel('Query Latency (ms)')
        plt.title(f'RAG Speed: Brute Force vs. Tree Index ({metrics["num_chunks"]} Chunks)')
        
        # Add a note about build time for the tree
        plt.figtext(0.5, 0.01, f"BallTree Index Build Time: {metrics['balltree_build']:.2f}ms", 
                    ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        plt.show()
