"""
Setup Vector Database
=====================
Initialize ChromaDB and populate with restaurant documents.
Run this script before using scripts 05 and 06 that have RAG capabilities.

Usage:
    python scripts/utils/setup_vectordb.py

This will:
1. Load markdown documents (FAQ, catering, wine list)
2. Chunk them intelligently by headers
3. Generate embeddings
4. Store in ChromaDB
"""

import os
from pathlib import Path
import re
from typing import List, Dict

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("ERROR: Required packages not installed")
    print("Install with: pip install chromadb sentence-transformers")
    exit(1)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "restaurant"
CHROMA_DIR = BASE_DIR / "data" / "embeddings"

# Files to embed
DOCUMENTS = {
    "faq.md": "FAQ",
    "catering.md": "Catering",
    "wine_list.md": "Wine List"
}


def load_markdown_file(filepath: Path) -> str:
    """Load markdown file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return ""


def chunk_by_headers(content: str, source: str, max_chunk_size: int = 1000) -> List[Dict]:
    """
    Chunk markdown content by headers.
    Keeps related content together under each header.
    """
    chunks = []

    # Split by major headers (## or ###)
    sections = re.split(r'\n(#{1,3})\s+(.+)\n', content)

    current_section = ""
    current_header = ""
    section_level = 0

    for i in range(0, len(sections)):
        part = sections[i]

        # Check if this is a header marker (##, ###, etc.)
        if part.startswith('#') and i + 1 < len(sections):
            # Save previous section if it exists
            if current_section.strip():
                chunks.append({
                    "content": current_section.strip(),
                    "source": source,
                    "section": current_header,
                    "level": section_level
                })

            # Start new section
            section_level = len(part)
            current_header = sections[i + 1].strip()
            current_section = ""

        elif not part.startswith('#'):
            # Add content to current section
            current_section += part

            # If section is getting too long, chunk it
            if len(current_section) > max_chunk_size:
                # Try to split on paragraph breaks
                paragraphs = current_section.split('\n\n')
                if len(paragraphs) > 1:
                    # Save first chunk
                    chunks.append({
                        "content": '\n\n'.join(paragraphs[:-1]).strip(),
                        "source": source,
                        "section": current_header,
                        "level": section_level
                    })
                    # Keep last paragraph for next chunk
                    current_section = paragraphs[-1]

    # Don't forget the last section
    if current_section.strip():
        chunks.append({
            "content": current_section.strip(),
            "source": source,
            "section": current_header,
            "level": section_level
        })

    # Filter out very small chunks
    chunks = [c for c in chunks if len(c['content']) > 50]

    return chunks


def main():
    """Main setup function"""
    print("=" * 60)
    print("Setting up Vector Database for Bella's Italian Restaurant")
    print("=" * 60)

    # Ensure output directory exists
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize embedding model
    print("\n[1/4] Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Model loaded: all-MiniLM-L6-v2")

    # Initialize ChromaDB
    print("\n[2/4] Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if it exists
    try:
        client.delete_collection(name="restaurant_docs")
        print("✓ Deleted existing collection")
    except:
        pass

    # Create new collection
    collection = client.create_collection(
        name="restaurant_docs",
        metadata={"description": "Restaurant knowledge base documents"}
    )
    print("✓ Created new collection: restaurant_docs")

    # Process each document
    print("\n[3/4] Processing documents...")
    all_chunks = []

    for filename, doc_type in DOCUMENTS.items():
        filepath = DATA_DIR / filename

        if not filepath.exists():
            print(f"⚠ Skipping {filename} - file not found")
            continue

        print(f"\n  Processing {filename}...")

        # Load content
        content = load_markdown_file(filepath)
        if not content:
            print(f"  ⚠ No content in {filename}")
            continue

        # Chunk content
        chunks = chunk_by_headers(content, doc_type, max_chunk_size=800)
        print(f"  ✓ Created {len(chunks)} chunks from {doc_type}")

        all_chunks.extend(chunks)

    print(f"\n  Total chunks created: {len(all_chunks)}")

    # Generate embeddings and store
    print("\n[4/4] Generating embeddings and storing...")

    if not all_chunks:
        print("ERROR: No chunks to process!")
        return

    # Prepare data for insertion
    documents = [chunk['content'] for chunk in all_chunks]
    metadatas = [
        {
            "source": chunk['source'],
            "section": chunk['section'],
            "level": chunk['level']
        }
        for chunk in all_chunks
    ]
    ids = [f"doc_{i}" for i in range(len(all_chunks))]

    # Generate embeddings
    print(f"  Generating {len(documents)} embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True).tolist()

    # Add to collection
    print("  Storing in ChromaDB...")
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print("  ✓ All documents stored successfully")

    # Verify
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"  - Total documents: {collection.count()}")
    print(f"  - Embedding model: all-MiniLM-L6-v2")
    print(f"  - Storage location: {CHROMA_DIR}")

    print(f"\n📝 Indexed documents:")
    for doc_type in set(chunk['source'] for chunk in all_chunks):
        count = sum(1 for c in all_chunks if c['source'] == doc_type)
        print(f"  - {doc_type}: {count} chunks")

    print(f"\n✅ Vector database ready!")
    print(f"   You can now run scripts 05 and 06 with RAG capabilities.")

    # Test retrieval
    print(f"\n🧪 Testing retrieval...")
    test_query = "Do you do catering for weddings?"
    test_embedding = model.encode(test_query).tolist()

    results = collection.query(
        query_embeddings=[test_embedding],
        n_results=2
    )

    if results and results['documents']:
        print(f"  Query: \"{test_query}\"")
        print(f"  Found {len(results['documents'][0])} relevant chunks:")
        for i, doc in enumerate(results['documents'][0], 1):
            metadata = results['metadatas'][0][i-1]
            print(f"    {i}. {metadata['source']} - {metadata['section'][:50]}...")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
