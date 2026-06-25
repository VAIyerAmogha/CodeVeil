from app.ingestion.ast_chunker import chunk_repo
from app.ingestion.fallback_chunker import chunk_file_fallback

# TypeScript test
with open('/tmp/test.ts', 'w') as f:
    f.write('function greet(name: string): string { return \`Hello \${name}\`; }')
chunks = chunk_repo('/tmp/test.ts', 'TypeScript')
print('TS chunks:', len(chunks), chunks[0]['chunk_type'])

# Fallback test
with open('/tmp/test.go', 'w') as f:
    f.write('\n'.join([f'line {i}' for i in range(200)]))
chunks = chunk_file_fallback('/tmp/test.go',language='Go')
print('fallback chunks:', len(chunks))

# Guard test — fallback must reject Python
try:
    chunk_file_fallback('/tmp/test.py', language='Python')
    print('FAIL — should have raised')
except RuntimeError as e:
    print('guard ok:', e)
