import uuid
import os
import json
import threading
from queue import Queue
import time
from functools import wraps
import pandas as pd
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
# import google.generativeai as genai  # Removed deprecated package

from flask import Flask, request, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename
from flask_cors import CORS

from agents.answerKeyAgent.answerKeyAgent import answerKeyAgent
from agents.answerKeyAgent.documentProcessor import documentProcessor  # If needed for processing docs
from ragSystems.imageRag import ClipSearchService  # If needed for indexing images

from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator
from data.events import get_events
from dummyDB import JSONStorage

app = Flask(__name__)
# Allow CORS for all origins, just like both apps did previously
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Cache-Control", "Accept", "ngrok-skip-browser-warning"],
        "supports_credentials": False
    }
})

# ==========================================
# Answer Key Agent Configuration
# ==========================================
UPLOAD_FOLDER = r'D:\scoriX_agent\data'
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'question_papers')
DOC_FOLDER = os.path.join(UPLOAD_FOLDER, 'answer_keys')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(DOC_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}

# ==========================================
# Question Paper Generator Configuration
# ==========================================
import threading
json_storage = JSONStorage()
active_tasks = {}
task_results = {}
task_locks = {}
session_store = {}
answerkey_store = {}
answerkey_tasks = {}

# ==========================================
# Helpers for Answer Key Agent
# ==========================================
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

def save_images(files):
    print(f"🔍 Checking for images in request...")
    print(f"📁 Request files keys: {list(request.files.keys())}")
    print(f"📁 Request form keys: {list(request.form.keys())}")
    
    if 'images' not in request.files:
        print("⚠️ No 'images' field found in request.files")
        return []
        
    image_files = request.files.getlist('images')
    print(f"📸 Found {len(image_files)} image files")
    
    image_paths = []
    for i, file in enumerate(image_files):
        print(f"📸 Processing file {i+1}: {file.filename}")
        
        if file.filename == '':
            print(f"⚠️ File {i+1} has empty filename, skipping")
            continue
            
        if not allowed_image(file.filename):
            print(f"⚠️ File {i+1} ({file.filename}) not allowed, skipping")
            continue
            
        filename = secure_filename(file.filename)
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
        try:
            file.save(filepath)
            image_paths.append(filepath)
            print(f"✅ Saved file {i+1}: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save file {i+1}: {e}")
            
    print(f"📸 Total saved images: {len(image_paths)}")
    return image_paths

def run_answer_key_task(task_id, session_id, image_paths):
    try:
        print(f"[TASK STARTED] {task_id}")
        print(f"Session ID: {session_id}")
        print(f"Image paths: {image_paths}")

        # Check if image paths are provided
        if not image_paths:
            print("⚠️ No image paths provided!")
            answerkey_tasks[task_id] = {
                "status": "error",
                "error": "No images provided for processing"
            }
            print(f"[TASK FAILED] {task_id} - No images")
            return

        agent = answerKeyAgent(uniqID=session_id, notesProvided=False)
        print("✅ Answer key agent created successfully")

        print("🔄 Starting answer key generation...")
        response = agent.answerKeyAgent(
            questionPaperPaths=image_paths,
            simpleAnswerSheet=False
        )
        
        print(f"📋 Agent response: {response}")
        print(f"📋 Response type: {type(response)}")
        print(f"📋 Response length: {len(response) if response else 'None'}")

        # Check if response is valid
        if not response:
            print("⚠️ Empty response from answer key agent!")
            answerkey_tasks[task_id] = {
                "status": "error",
                "error": "Answer key agent returned empty response"
            }
            print(f"[TASK FAILED] {task_id} - Empty response")
            return

        answerkey_tasks[task_id] = {
            "status": "completed",
            "result": response
        }

        answerkey_store[session_id] = response

        print(f"[TASK COMPLETED] {task_id}")

    except Exception as e:
        import traceback
        print(f"❌ Error in answer key task: {e}")
        traceback.print_exc()

        answerkey_tasks[task_id] = {
            "status": "error",
            "error": str(e)
        }

        print(f"[TASK FAILED] {task_id} - Exception: {e}")
        
def save_docs(files):
    if 'docs' not in request.files:
        return []
    doc_files = request.files.getlist('docs')
    doc_paths = []
    for file in doc_files:
        if file.filename == '':
            continue
        if not allowed_doc(file.filename):
            continue
        filename = secure_filename(file.filename)
        filepath = os.path.join(DOC_FOLDER, filename)
        file.save(filepath)
        doc_paths.append(filepath)
    return doc_paths

def save_ordered_images(image_files):
    image_paths = []
    for idx, file in enumerate(image_files):
        if file.filename == '':
            continue
        if not allowed_image(file.filename):
            continue
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_{idx}{ext}"
        filepath = os.path.join("D:\\scoriX_agent\\data\\answer_sheets", new_filename)
        file.save(filepath)
        image_paths.append(filepath)
    return image_paths

# ==========================================
# Helpers for Question Paper Generator
# ==========================================
def generate_task_id():
    return str(uuid.uuid4())

def run_question_paper_generation(task_id, text, file_path):
    try:
        print(f"\n{'='*80}")
        print(f"[GENERATION START] Task ID: {task_id}")
        print(f"{'='*80}\n")
        
        generator = QuestionPaperGenerator(collectionName=task_id)
        content_data, final_questions = generator.demoQuestionpaperGenerator(text, file_path)
        
        print("qpgeneration done in flask api")
        print(f"\n[DEBUG] Generation completed. Questions count: {len(final_questions)}")
        
        task_results[task_id] = {
            "status": "completed",
            "content_data": content_data,
            "questions": final_questions,
            "task_id": task_id
        }
        
        session_store[task_id] = {
            "question_paper": final_questions,
            "question_paper_summary": None,
            "chat_history": [],
            "created_at": time.time(),
            "last_updated": time.time()
        }
        
        print(f"\n{'='*80}")
        print(f"[SESSION CREATED] Session ID: {task_id}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Generation failed for task_id {task_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        task_results[task_id] = {
            "status": "error",
            "error": str(e),
            "task_id": task_id
        }
    finally:
        if task_id in active_tasks:
            del active_tasks[task_id]

def sse_error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            task_id = kwargs.get('task_id', 'unknown')
            print(f"[SSE GLOBAL ERROR] {task_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            def error_stream():
                yield f"data: {json.dumps({'status': 'error', 'error': f'Server error: {str(e)}'})}\n\n"
            return Response(
                stream_with_context(error_stream()),
                mimetype='text/event-stream',
                status=200,
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Expose-Headers': 'Content-Type'
                }
            )
    return decorated_function

def compare_question_papers(current_qp, new_qp):
    try:
        if len(current_qp) != len(new_qp):
            return True
        for i, (current_co, new_co) in enumerate(zip(current_qp, new_qp)):
            current_questions = set(current_co.get("questions", []))
            new_questions = set(new_co.get("questions", []))
            if current_questions != new_questions:
                return True
        return False
    except Exception:
        return True
def vishal_server(query,teacher_id):
    url = "http://192.168.219.88:5003/supervisor"

    payload = {
        "query": query,
        "teacher_id": teacher_id
    }

    try:
        response = requests.post(url, json=payload)
        response.json()
        if "question_paper" in response.json():
            json_storage.add("question_paper_history", response.json())
        elif "answer_key" in response.json():
            json_storage.add("answer_key_history", response.json())
        return response.json()
    except Exception as e:
        print("Error:", e)

import requests

def thanush_server(query, teacher_id,teacher_prompt, file_path):
    url = "http://192.168.219.88:5003/api/question-bank-generator"

    payload = {
        "teacher_prompt":teacher_prompt
    }

    files = {
        "file": open(file_path, "rb")
    }

    try:
        response = requests.post(url, data=payload, files=files)

        result = response.json()

        json_storage.add("question_paper_history", result.get("response"))

        return result

    except Exception as e:
        print("Error:", e)

@app.route("/api/answer_key_history", methods=["GET"])
def answer_key_history():
    return jsonify(json_storage.get("answer_key_history"))
    
@app.route("/api/question_paper_history", methods=["GET"])
def question_paper_history():  # Fixed function name
    return jsonify(json_storage.get("question_paper_history"))

@app.route("/api/chat_application", methods=['POST'])
def chat_application():
    try:
        # Debug logging
        print(f"🔍 Request form data: {dict(request.form)}")
        print(f"🔍 Request files: {list(request.files.keys())}")
        
        agent_mode = request.form.get("agent_mode")
        print(f"🔍 Agent mode received: '{agent_mode}' (type: {type(agent_mode)})")

        if agent_mode == "general":
            query = request.form.get("query")
            teacher_id = request.form.get("class_room_id")
            print(f"🔍 General mode - Query: '{query}', Teacher ID: '{teacher_id}'")
            return jsonify(vishal_server(query, teacher_id))
            
        elif agent_mode == "question_paper":
            query = request.form.get("teacher_Prompt")
            teacher_id = request.form.get("class_room_id")

            file = request.files.get("file")

            file_path = None

            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

            return jsonify(thanush_server(query, teacher_id, query, file_path))
                    
        elif agent_mode == "answer_key":
            return start_answer_key()
            
        else:
            print(f"❌ Invalid agent mode: '{agent_mode}'")
            return jsonify({
                "status": "error",
                "message": f"Invalid agent mode: '{agent_mode}'. Valid modes: 'general', 'question_paper', 'answer_key'"
            }), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "message": f"Server error: {str(e)}"
        }), 500











@app.route('/api/answer_key_generator', methods=['POST'])
def start_answer_key():

    try:
        session_id = request.form.get("class_room_id")
        print("you are in")

        if not session_id:
            session_id = str(uuid.uuid4())

        # If already generated
        if session_id in answerkey_store:
            return jsonify({
                "status": "completed",
                "result": answerkey_store[session_id]
            })

        image_paths = save_images(request.files)

        task_id = str(uuid.uuid4())

        answerkey_tasks[task_id] = {
            "status": "processing"
        }

        thread = threading.Thread(
            target=run_answer_key_task,
            args=(task_id, session_id, image_paths)
        )

        thread.start()

        return jsonify({
            "task_id": task_id,
            "status": "processing"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/answer_key/status/<task_id>', methods=['GET'])
def answer_key_status(task_id):

    if task_id not in answerkey_tasks:
        return jsonify({
            "status": "error",
            "message": "Task not found"
        }), 404

    return jsonify(answerkey_tasks[task_id])

@app.route("/api/get-answer-key/<classroom_id>", methods=["GET"])
def get_answer_key_from_session(classroom_id):
    try:
        if not classroom_id in answerkey_store:
            return jsonify({"message" : "no class room found"}) , 404
        else:
            return jsonify({"message":"answerkey fetched successfully","answerkey":answerkey_store[classroom_id]})
        
    except Exception as e:
        print("Error processing:", e)
        return jsonify({"error": str(e)}), 500
# ==========================================
# Routes for Question Paper Generator
# ==========================================
@app.route('/api/generate-question-paper', methods=['POST'])
def generate_question_paper():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            text = request.form.get('text') if request.form else None
            file_path = request.form.get('file_path') if request.form else None
            if not text and request.files:
                text_file = request.files.get('text')
                if text_file:
                    text = text_file.read().decode('utf-8') if text_file.filename else None
            data = {'text': text, 'file_path': file_path}
        
        if not data or not data.get('text'):
            return jsonify({"error": "Missing required field: 'text'"}), 400
        
        text = data['text']
        file_path = data.get('file_path', None)
        task_id = generate_task_id()
        
        active_tasks[task_id] = {"status": "running", "started_at": time.time()}
        
        thread = threading.Thread(
            target=run_question_paper_generation,
            args=(task_id, text, file_path),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            "task_id": task_id,
            "message": "Question paper generation started",
            "stream_url": f"/api/stream/{task_id}"
        }), 202
        
    except Exception as e:
        print(f"[ERROR] Endpoint failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream/<task_id>')
@sse_error_handler
def stream_events(task_id):
    if task_id not in active_tasks and task_id not in task_results:
        def error_stream():
            yield f"data: {json.dumps({'status': 'error', 'error': 'Task not found or expired'})}\n\n"
        return Response(
            stream_with_context(error_stream()),
            mimetype='text/event-stream',
            status=200,
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

    def event_stream():
        last_idx = 0
        try:
            while True:
                events, last_idx = get_events(task_id, last_idx)
                for event in events:
                    yield f"data: {json.dumps(event)}\n\n"
                
                if task_id in task_results:
                    result = task_results[task_id]
                    if result["status"] == "completed":
                        yield f"data: {json.dumps({'status': 'completed', 'task_id': task_id})}\n\n"
                        break
                    elif result["status"] == "error":
                        yield f"data: {json.dumps({'status': 'error', 'error': result['error']})}\n\n"
                        break
                time.sleep(0.5)
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        status=200,
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@app.route('/api/result/<task_id>', methods=['GET'])
def get_result(task_id):
    if task_id in task_results:
        return jsonify(task_results[task_id]), 200
    elif task_id in active_tasks:
        return jsonify({
            "status": "running",
            "task_id": task_id,
            "message": "Task is still running"
        }), 202
    else:
        return jsonify({"status": "not_found", "error": "Task not found"}), 404

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    # Check question paper generation tasks
    if task_id in task_results:
        return jsonify({"status": task_results[task_id]["status"], "task_id": task_id}), 200
    elif task_id in active_tasks:
        return jsonify({"status": "running", "task_id": task_id}), 200
    # Check answer key generation tasks
    elif task_id in answerkey_tasks:
        return jsonify(answerkey_tasks[task_id]), 200
    else:
        return jsonify({"status": "not_found", "task_id": task_id}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({"error": "Missing required fields: 'session_id' and 'message'"}), 400
        
        session_id = data['session_id']
        message = data['message']
        
        if session_id not in session_store:
            return jsonify({"error": "Session not found."}), 404
            
        session = session_store[session_id]
        chat_history = session['chat_history'][-3:] if len(session['chat_history']) > 0 else None
        generator = QuestionPaperGenerator(collectionName=session_id)
        
        result = generator.chatAgent(
            input=message,
            questionPaperSummarizer=session['question_paper_summary'],
            currentQuestionPaper=session['question_paper'],
            sessionHistory=chat_history
        )
        
        answer = result.get("answer")
        result_qp = result.get("question_summary")
        
        session['chat_history'].append({"role": "user", "content": message})
        if answer:
            session['chat_history'].append({"role": "assistant", "content": answer})
            
        updated = False
        if result_qp:
            updated = compare_question_papers(session['question_paper'], result_qp)
            if updated:
                session['question_paper_summary'] = None
                session['question_paper'] = result_qp
        
        response_type = "mixed"
        if updated and not answer:
            response_type = "qp_update"
        elif answer and not updated:
            response_type = "direct_answer"
            
        return jsonify({
            "session_id": session_id,
            "type": response_type,
            "answer": answer,
            "question_paper": session['question_paper'],
            "changes_made": updated
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in session_store:
        return jsonify({"error": "Session not found"}), 404
    session = session_store[session_id]
    return jsonify({
        "session_id": session_id,
        "question_paper": session['question_paper'],
        "chat_history": session['chat_history'],
        "created_at": session['created_at'],
        "last_updated": session['last_updated']
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "active_tasks": len(active_tasks),
        "completed_tasks": len(task_results),
        "active_sessions": len(session_store)
    }), 200



mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["scorix"]
collection = db["student_list"]
classroom_collection = db["classrooms"]



@app.route('/upload', methods=['POST'])
def upload_file():

    classroom_id = request.form.get("classroom_id")

    if not classroom_id:
        return jsonify({"error": "classroom_id is required"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:

        # Read Excel
        df = pd.read_excel(file, engine='openpyxl')
        df = df.fillna('')

        data = df.to_dict(orient='records')

        # Insert student list
        document = {
            "nameList": data
        }

        result = collection.insert_one(document)

        student_list_id = result.inserted_id

        # Update classroom document
        classroom_collection.update_one(
            {"_id": ObjectId(classroom_id)},
            {"$push": {"nameList": student_list_id}}
        )
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)
