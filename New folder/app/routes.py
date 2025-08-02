routes = Blueprint('routes', __name__)
from flask import Blueprint, request, jsonify, current_app
import os
import openai
from app.utils import allowed_file, save_file, extract_text_from_pdf
from app.models import Document, Chunk
from app.db import SessionLocal

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@routes.route('/upload', methods=['POST'])
def upload_documents():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({'error': 'No files uploaded'}), 400
    if len(files) > 20:
        return jsonify({'error': 'Cannot upload more than 20 documents at once'}), 400

    session = SessionLocal()
    uploaded = []
    for file in files:
        if not allowed_file(file.filename):
            continue
        file_path = save_file(file, UPLOAD_FOLDER)
        texts = extract_text_from_pdf(file_path)
        num_pages = len(texts)
        if num_pages > 1000:
            os.remove(file_path)
            continue
        doc = Document(filename=file.filename, num_pages=num_pages)
        session.add(doc)
        session.flush()  # get doc.id
        # Chunking: here, 1 page = 1 chunk (can be improved)
        for idx, text in enumerate(texts):
            chunk = Chunk(document_id=doc.id, chunk_index=idx, text=text, embedding_id=None)
            session.add(chunk)
        uploaded.append({'filename': file.filename, 'num_pages': num_pages})
    session.commit()
    session.close()
    return jsonify({'uploaded': uploaded}), 200


@routes.route('/query', methods=['POST'])
def query_system():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Retrieve top relevant chunks (simple keyword match for demo)
    session = SessionLocal()
    chunks = session.query(Chunk).all()
    # Score chunks by keyword overlap
    scored = []
    for chunk in chunks:
        score = sum(1 for word in query.lower().split() if word in (chunk.text or '').lower())
        if score > 0:
            scored.append((score, chunk))
    # Sort and select top 5
    top_chunks = [c.text for _, c in sorted(scored, reverse=True)[:5]]
    session.close()

    # Prepare context for LLM
    context = '\n---\n'.join(top_chunks) if top_chunks else 'No relevant context found.'

    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        return jsonify({'error': 'OpenAI API key not set'}), 500
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                {"role": "user", "content": f"Context: {context}\nQuestion: {query}\nAnswer the question based only on the context above."}
            ],
            max_tokens=256
        )
        answer = response.choices[0].message['content'].strip()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'query': query, 'answer': answer, 'chunks': top_chunks}), 200

@routes.route('/documents', methods=['GET'])
def list_documents():
    session = SessionLocal()
    docs = session.query(Document).all()
    result = []
    for doc in docs:
        result.append({
            'id': doc.id,
            'filename': doc.filename,
            'upload_time': doc.upload_time.isoformat(),
            'num_pages': doc.num_pages
        })
    session.close()
    return jsonify({'documents': result}), 200
