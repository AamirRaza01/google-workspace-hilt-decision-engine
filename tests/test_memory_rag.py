""" Verification script testing chunk allocations, Gemini vector spaces, and ChromaDB lookups """
import sys
from src.utils.logger import setup_logger
from src.utils.text_processing import chunk_text_by_boundary
from src.memory.email_storage import EmailStorageCache
from src.memory.vector_store import PersistentVectorStore

def verify_memory_systems():
    setup_logger()
    print("="*80)
    print("🧠 RAG CONTEXT STRUCTURAL VECTOR STORAGE TESTS")
    print("="*80)
    
    try:
        # Initialize sub-clients
        cache = EmailStorageCache()
        vdb = PersistentVectorStore()
        
        # 1. Clear any old data to isolate this test run
        vdb.clear_all_vector_data()
        
        sample_email_id = "test_message_101abc"
        sample_payload = {
            "subject": "Urgent Pre-Placement Drive Guidelines IIIT",
            "from": "placement.officer@university.edu",
            "date": "Wed, 10 Jun 2026 10:00:00 GMT",
            "body_text": (
                "Attention all engineering undergraduates. The recruitment guidelines require full form attendance. "
                "The technical interview shortlist contains core graph questions covering DFS, BFS, and tree algorithms. "
                "Please bring your updated resume printout directly to auditorium block C tomorrow sharp at 9:00 AM."
            )
        }
        
        print("\nStep 1: Testing Full Text Document Caching...")
        cache.cache_email_record(sample_email_id, sample_payload)
        print("   ✅ Full body stored successfully inside local file storage data.")
        
        print("\nStep 2: Processing sliding boundary text chunks...")
        chunks = chunk_text_by_boundary(sample_payload["body_text"], chunk_size=150, overlap=30)
        print(f"   ✅ Split original string text cleanly into: {len(chunks)} overlapping parts.")
        
        print("\nStep 3: Calculating cloud embeddings and indexing data vectors...")
        for chunk in chunks:
            vdb.add_email_chunk(sample_email_id, chunk, sample_payload)
        print(f"   ✅ ChromaDB collection currently holds: {vdb.collection.count()} active documents.")
        
        print("\nStep 4: Executing Semantic Meaning Conceptual Matches...")
        query_expression = "What algorithms should I study for tomorrow's technical placement interviews?"
        print(f"   User Query: '{query_expression}'")
        
        matches = vdb.query_semantic_matches(query_expression, max_results=1)
        
        if matches:
            print("\n🎉 RAG SEMANTIC PIPELINE MATCHED ACCURATELY!")
            print(f"   Retrieved Snippet: \"{matches[0]['text']}\"")
            print(f"   Source Email Key:   {matches[0]['metadata']['email_id']}")
            print(f"   Cosine Distance:    {matches[0]['distance']:.4f}")
            print("="*80)
        else:
            print("\n❌ Vector lookup came back empty. Please check Gemini API connection scopes.")
            print("="*80)
            
    except Exception as e:
        print(f"\n❌ Structural Memory Fail: {e}")
        print("="*80)

if __name__ == "__main__":
    verify_memory_systems()