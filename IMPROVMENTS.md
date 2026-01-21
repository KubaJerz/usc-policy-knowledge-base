# What can be done to improve

## [x] 1. Basic Rag
Done

**PROBLEM**:MAny of our embeddings are dense so poor retrival

## [] 2. Better Chunking
- semantic (maybe)
- fixed size breakpoint or fixed size (we need to split up the docs they are too big)
    - https://arxiv.org/abs/2410.13070


## [] 3. Hybrid Search (Semantic + Lexical)
- Dense Vector Search: For semantic understanding ("How do I reset the system?").
- Lexical Search (BM25/SPLADE): For keyword exact-matching ("Error code 0x543").

These we do fusion on this so use a model like Weaviate, Qdrant, or Elasticsearch > Chroma

## [] 4. GraphRAG
- SOTA
- High accuracy when we dont jsut want facts but the facts have relatinoships 

## [] WE NEED A PROPER EVAL