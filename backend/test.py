
from app.retrieval.bm25_retriever import retrieve_bm25
from app.retrieval.dense_retriever import retrieve_dense

# Replace with a repo_id you indexed in Phase 2
REPO_ID = 'your-repo-id-here'
QUERY = 'how does authentication work'

bm25_results = retrieve_bm25(REPO_ID, QUERY, top_k=20)
print(f'BM25 results: {len(bm25_results)}')
print(f'Top BM25: {bm25_results[0]}')
assert len(bm25_results) <= 20
assert 'chunk_id' in bm25_results[0]
assert 'score' in bm25_results[0]

dense_results = retrieve_dense(REPO_ID, QUERY, top_k=20)
print(f'Dense results: {len(dense_results)}')
print(f'Top dense: {dense_results[0]}')
assert len(dense_results) <= 20
assert 'chunk_id' in dense_results[0]
assert 'score' in dense_results[0]

print('all checks passed')
