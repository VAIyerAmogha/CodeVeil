import asyncio
from app.ingestion.embedder import embed_texts, embed_query
async def test():
    vecs = await embed_texts(['def hello(): pass', 'class Foo: pass'])
    print(f'batch: {len(vecs)} vectors, dim={len(vecs[0])}')
    assert len(vecs[0]) == 768, f'Wrong dim: {len(vecs[0])}'
    q = await embed_query('what does hello do')
    print(f'query: dim={len(q)}')
    assert len(q) == 768
    print('ALL OK')
asyncio.run(test())