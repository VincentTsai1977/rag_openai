from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Define vector store ID and assistant ID
VECTOR_STORE_ID = os.getenv('VECTOR_STORE_ID')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')

@app.route('/get_vector_store', methods=['GET'])
def get_vector_store():
    try:
        vector_store = client.beta.vector_stores.retrieve(vector_store_id=VECTOR_STORE_ID)
        return jsonify({"status": "success", "data": vector_store})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_vector_store_files', methods=['GET'])
def get_vector_store_files():
    try:
        vector_store_files = client.beta.vector_stores.files.list(vector_store_id=VECTOR_STORE_ID)
        return jsonify({"status": "success", "data": vector_store_files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_assistant', methods=['GET'])
def get_assistant():
    try:
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        return jsonify({"status": "success", "data": assistant})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/query_assistant', methods=['POST'])
def query_assistant():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({"status": "error", "message": "Query is required"}), 400

        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = next((msg for msg in messages if msg.role == 'assistant'), None)

        if assistant_message:
            return jsonify({"status": "success", "response": assistant_message.content[0].text.value})
        else:
            return jsonify({"status": "error", "message": "No response from assistant"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Replit-specific code
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)