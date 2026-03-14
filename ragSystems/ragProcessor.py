from ragSystems.embedder import TextEmbedder, HybridEmbedder
from ragSystems.qdrantManager import QdrantManager, HybridQdrantManager



class ragProcessor:
    def __init__(self,collection_name):
        self.textEmbedder = TextEmbedder()
        self.qdrantManager = QdrantManager(collection_name=collection_name)

    def docStoring(self,chunks):
        embeddings = self.textEmbedder.embedChunksInMultiVector(chunks)
        spares = self.textEmbedder.getSparsEmbeddings(chunks)
        self.qdrantManager.upsertPoints(embeddings, spares, chunks,)

    def search(self,query):
        embeddings = self.textEmbedder.multiVectorEmbedder(query)
        spares = self.textEmbedder.getSparsEmbeddings(query)
        result = self.qdrantManager.hybrid_search(embeddings, spares)
        output = ""
        for r in result.points:
            output += r.payload['text']
            output += "\n"

        return output


class HybridRagProcessor:
    def __init__(self, collection_name="rag_hybrid_final"):
        self.textEmbedder = HybridEmbedder()
        self.qdrantManager = HybridQdrantManager(collection_name=collection_name)

    def process_and_store(self, chunks: list[str], metadata: list[dict]):
        """
        Process text chunks and store them with metadata.
        chunks: List of text strings.
        metadata: List of dicts corresponding to chunks.
        """
        print("Embeddings generation started...")
        dense_vecs = self.textEmbedder.embed_text(chunks)
        sparse_vecs = self.textEmbedder.get_sparse_embeddings(chunks)
        print("Embeddings generated.")
        
        self.qdrantManager.upsert_integrated_hybrid(dense_vecs, sparse_vecs, metadata)

    def search(self, query, metadata_filter: dict = None, top_k: int = 3):
        """
        Search for query with optional metadata filtering.
        Uses DENSE-ONLY search to avoid sparse vector encoding issues.
        """
        # Validate query (allow 2+ chars for queries like "AI", "ML", "CO", "PO")
        if not query or not isinstance(query, str) or len(query.strip()) < 2:
            print(f"⚠️ Warning: Query too short or invalid: '{query}'. Returning empty results.")
            return []
        
        try:
            # Generate dense embedding only
            dense_vec = self.textEmbedder.embed_text(query)[0]
            
            # Use dense-only search (more reliable)
            return self._dense_only_search(dense_vec, metadata_filter, top_k)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error during search: {error_msg}")
            import traceback
            traceback.print_exc()
            return []

    
    def _dense_only_search(self, dense_vec, metadata_filter: dict = None, top_k: int = 3):
        """
        Fallback search using only dense vectors (no sparse/BM25).
        Uses the search method which properly supports named vectors.
        """
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue
            
            # Build filter if metadata_filter is provided
            query_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Convert dense_vec to list if it's a numpy array
            dense_vec_list = dense_vec.tolist() if hasattr(dense_vec, 'tolist') else dense_vec
            
            # Use query_points with named vector "dense" (collection has both dense and sparse)
            results = self.qdrantManager.client.query_points(
                collection_name=self.qdrantManager.collection_name,
                query=dense_vec_list,
                using="dense",  # Specify which named vector to use
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            )
            
            output = []
            for r in results.points:
                output.append(r.payload)
            
            print(f"   ✅ Dense-only search returned {len(output)} results")
            return output
            
        except Exception as e:
            print(f"❌ Dense-only search failed: {e}")
            import traceback
            traceback.print_exc()
            return []
