from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import uuid
import json
import threading
from queue import Queue
from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator
from data.events import get_events
import time
from functools import wraps  # For error handler decorator
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Any website can call (dev-only; tighten for prod)
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Cache-Control", "Accept", "ngrok-skip-browser-warning"],
        "supports_credentials": False
    }
})

# Store active tasks and their results
active_tasks = {}
task_results = {}
task_locks = {}

# Session storage (session_id = task_id)
session_store = {}

def generate_task_id():
    """Generate a unique task ID"""
    return str(uuid.uuid4())

def run_question_paper_generation(task_id, text, file_path):
    """
    Background thread function to run question paper generation
    """
    try:
        print(f"\n{'='*80}")
        print(f"[GENERATION START] Task ID: {task_id}")
        print(f"{'='*80}\n")
        
        # Create QuestionPaperGenerator instance with the task_id
        generator = QuestionPaperGenerator(collectionName=task_id)
        
        # Run the generation process
        content_data, final_questions = generator.demoQuestionpaperGenerator(text, file_path)
        print("qpgeneration done in flask api")
        
        print(f"\n[DEBUG] Generation completed. Questions count: {len(final_questions)}")
        print(f"[DEBUG] Final questions structure: {type(final_questions)}")
        
        # Store the result
        task_results[task_id] = {
            "status": "completed",
            "content_data": content_data,
            "questions": final_questions,
            "task_id": task_id
        }
        
        print(f"[DEBUG] Task result stored for task_id: {task_id}")
        
        # Automatically create session (session_id = task_id)
        session_store[task_id] = {
            "question_paper": final_questions,
            "question_paper_summary": None,  # Will be generated on first chat
            "chat_history": [],
            "created_at": time.time(),
            "last_updated": time.time()
        }
        
        print(f"\n{'='*80}")
        print(f"[SESSION CREATED] Session ID: {task_id}")
        print(f"[SESSION CREATED] Question paper stored: {len(final_questions)} COs")
        print(f"[SESSION CREATED] Total sessions in store: {len(session_store)}")
        print(f"[SESSION CREATED] Session store keys: {list(session_store.keys())}")
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
        # Mark task as no longer active
        if task_id in active_tasks:
            del active_tasks[task_id]
            print(f"[DEBUG] Task {task_id} removed from active_tasks")

@app.route('/api/generate-question-paper', methods=['POST'])
def generate_question_paper():
    """
    Start question paper generation and return task ID
    
    Request body (JSON or form data):
    {
        "text": "Course outcomes and program outcomes text",
        "file_path": "optional/path/to/pdf" (optional)
    }
    
    Response:
    {
        "task_id": "unique-task-id",
        "message": "Question paper generation started"
    }
    """
    # Temporary debug logging (remove after fixing)
    print(f"[DEBUG] Content-Type: {request.content_type}")
    print(f"[DEBUG] Raw body: {request.get_data(as_text=True)}")
    print(f"[DEBUG] Is JSON? {request.is_json}")
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            print("Parsed as JSON:", data)
        else:
            # Parse form data (urlencoded or multipart)
            text = request.form.get('text') if request.form else None
            file_path = request.form.get('file_path') if request.form else None
            
            # If 'text' is sent as a file (e.g., PDF upload), handle it
            if not text and request.files:
                text_file = request.files.get('text')
                if text_file:
                    text = text_file.read().decode('utf-8') if text_file.filename else None
            
            data = {
                'text': text,
                'file_path': file_path
            }
            print("Parsed as form data:", data)
        
        if not data or not data.get('text'):
            return jsonify({
                "error": "Missing required field: 'text'"
            }), 400
        
        text = data['text']
        file_path = data.get('file_path', None)
        
        # Generate unique task ID
        task_id = generate_task_id()
        
        # Mark task as active
        active_tasks[task_id] = {
            "status": "running",
            "started_at": time.time()
        }
        
        # Start generation in background thread
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
        traceback.print_exc()  # Logs full stack trace to console
        return jsonify({
            "error": str(e)
        }), 500
        
# Optional: Global error handler for SSE routes (catches everything)
def sse_error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"[SSE GLOBAL ERROR] {task_id if 'task_id' in kwargs else 'unknown'}: {str(e)}")
            import traceback
            traceback.print_exc()
            def error_stream():
                yield f"data: {json.dumps({'status': 'error', 'error': f'Server error: {str(e)}'})}\n\n"
            return Response(
                stream_with_context(error_stream()),
                mimetype='text/event-stream',
                status=200,  # Always 200, even errors
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Expose-Headers': 'Content-Type'
                }
            )
    return decorated_function

@app.route('/api/stream/<task_id>')
@sse_error_handler  # Wraps the whole function
def stream_events(task_id):
    # Early task check - now SSE-safe
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
                # Your get_events call - if this fails, decorator catches it
                events, last_idx = get_events(task_id, last_idx)
                
                for event in events:
                    yield f"data: {json.dumps(event)}\n\n"  # Assume event has 'msg'
                
                if task_id in task_results:
                    result = task_results[task_id]
                    if result["status"] == "completed":
                        yield f"data: {json.dumps({'status': 'completed', 'task_id': task_id})}\n\n"
                        break
                    elif result["status"] == "error":
                        yield f"data: {json.dumps({'status': 'error', 'error': result['error']})}\n\n"
                        break
                
                time.sleep(0.5)
        except Exception as e:  # Local catch as backup
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
    """
    Get the final result of a completed task
    
    Response:
    {
        "status": "completed",
        "task_id": "unique-task-id",
        "content_data": [...],
        "questions": [...]
    }
    """
    if task_id in task_results:
        return jsonify(task_results[task_id]), 200
    elif task_id in active_tasks:
        return jsonify({
            "status": "running",
            "task_id": task_id,
            "message": "Task is still running"
        }), 202
    else:
        return jsonify({
            "status": "not_found",
            "error": "Task not found"
        }), 404

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    Get the current status of a task
    
    Response:
    {
        "status": "running" | "completed" | "error" | "not_found",
        "task_id": "unique-task-id"
    }
    """
    if task_id in task_results:
        return jsonify({
            "status": task_results[task_id]["status"],
            "task_id": task_id
        }), 200
    elif task_id in active_tasks:
        return jsonify({
            "status": "running",
            "task_id": task_id
        }), 200
    else:
        return jsonify({
            "status": "not_found",
            "task_id": task_id
        }), 404

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """
#     Send chat message and get response
    
#     Request body:
#     {
#         "session_id": "task_id",
#         "message": "Add 5 questions on loops"
#     }
    
#     Response types:
#     1. Direct answer: {"type": "direct_answer", "answer": "...", "session_id": "..."}
#     2. QP update: {"type": "qp_update", "question_paper": [...], "changes_made": true, "session_id": "..."}
#     3. Mixed: {"type": "mixed", "answer": "...", "question_paper": [...], "changes_made": true, "session_id": "..."}
#     """
#     try:
#         data = request.get_json()
        
#         if not data or 'session_id' not in data or 'message' not in data:
#             return jsonify({
#                 "error": "Missing required fields: 'session_id' and 'message'"
#             }), 400
        
#         session_id = data['session_id']
#         message = data['message']
        
#         print(f"\n{'='*80}")
#         print(f"[CHAT REQUEST] Session ID: {session_id}")
#         print(f"[CHAT REQUEST] Message: {message}")
#         print(f"[CHAT REQUEST] Available sessions: {list(session_store.keys())}")
#         print(f"[CHAT REQUEST] Session exists: {session_id in session_store}")
#         print(f"{'='*80}\n")
        
#         # Check if session exists
#         if session_id not in session_store:
#             print(f"[CHAT ERROR] Session {session_id} not found!")
#             print(f"[CHAT ERROR] Total sessions: {len(session_store)}")
#             print(f"[CHAT ERROR] Available session IDs: {list(session_store.keys())}")
#             return jsonify({
#                 "error": "Session not found. Generate a question paper first."
#             }), 404
        
#         session = session_store[session_id]
        
#         print(f"[CHAT DEBUG] Session found!")
#         print(f"[CHAT DEBUG] Question paper COs: {len(session['question_paper'])}")
#         print(f"[CHAT DEBUG] Chat history length: {len(session['chat_history'])}")
        
#         # Get last 3 interactions for context
#         chat_history = session['chat_history'][-3:] if len(session['chat_history']) > 0 else None
        
#         # Create QuestionPaperGenerator to access RAG collection
#         print(f"[CHAT DEBUG] Creating generator with collection: {session_id}")
#         generator = QuestionPaperGenerator(collectionName=session_id)
        
#         # Call chat agent
#         result = generator.chatAgent(
#             input=message,
#             questionPaperSummarizer=session['question_paper_summary'],
#             currentQuestionPaper=session['question_paper'],
#             sessionHistory=chat_history
#         )
        
#         # Determine response type based on what chatAgent returned
#         response_data = {"session_id": session_id}
        
#         # Type 1: Direct answer (returns tuple: answer, summary)
#         if isinstance(result, tuple) and len(result) == 2:
#             answer, qp_summary = result
            
#             # Store in chat history
#             session['chat_history'].append({"role": "user", "content": message})
#             session['chat_history'].append({"role": "assistant", "content": answer})
#             session['last_updated'] = time.time()
            
#             # Update summary cache
#             session['question_paper_summary'] = qp_summary
            
#             response_data.update({
#                 "type": "direct_answer",
#                 "answer": answer
#             })
        
#         # Type 2 & 3: QP update (returns QP) or Mixed (returns QP, answer)
#         else:
#             updated_qp = None
#             answer = None
            
#             # Check if it's mixed response (QP + answer)
#             if isinstance(result, tuple) and len(result) == 2:
#                 updated_qp, answer = result
#             else:
#                 # Just QP update
#                 updated_qp = result
            
#             # Compare question papers to detect changes
#             changes_made = False
#             if updated_qp:
#                 changes_made = compare_question_papers(session['question_paper'], updated_qp)
                
#                 if changes_made:
#                     # Update session QP
#                     session['question_paper'] = updated_qp
#                     # Invalidate summary (will regenerate on next call)
#                     session['question_paper_summary'] = None
            
#             # Store in chat history
#             session['chat_history'].append({"role": "user", "content": message})
            
#             if answer:
#                 # Mixed response
#                 session['chat_history'].append({
#                     "role": "assistant",
#                     "content": answer,
#                     "qp_updated": changes_made
#                 })
                
#                 response_data.update({
#                     "type": "mixed",
#                     "answer": answer,
#                     "question_paper": updated_qp,
#                     "changes_made": changes_made
#                 })
#             else:
#                 # QP update only
#                 session['chat_history'].append({
#                     "role": "assistant",
#                     "content": "Question paper updated",
#                     "qp_updated": changes_made
#                 })
                
#                 response_data.update({
#                     "type": "qp_update",
#                     "question_paper": updated_qp,
#                     "changes_made": changes_made
#                 })
            
#             session['last_updated'] = time.time()
        
#         return jsonify(response_data), 200
        
#     except Exception as e:
#         return jsonify({
#             "error": str(e)
#         }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({
                "error": "Missing required fields: 'session_id' and 'message'"
            }), 400
        
        session_id = data['session_id']
        message = data['message']
        print(f"\n{'='*80}")
        print(f"[CHAT REQUEST] Session ID: {session_id}")
        print(f"[CHAT REQUEST] Message: {message}")
        print(f"[CHAT REQUEST] Available sessions: {list(session_store.keys())}")
        print(f"[CHAT REQUEST] Session exists: {session_id in session_store}")
        print(f"{'='*80}\n")
        
        # Check if session exists
        if session_id not in session_store:
            print(f"[CHAT ERROR] Session {session_id} not found!")
            print(f"[CHAT ERROR] Total sessions: {len(session_store)}")
            print(f"[CHAT ERROR] Available session IDs: {list(session_store.keys())}")
            return jsonify({
                "error": "Session not found. Generate a question paper first."
            }), 404
        session = session_store[session_id]
        chat_history = session['chat_history'][-3:] if len(session['chat_history']) > 0 else None
        generator = QuestionPaperGenerator(collectionName=session_id)
        
        # Call chat agent
        result = generator.chatAgent(
            input=message,
            questionPaperSummarizer=session['question_paper_summary'],
            currentQuestionPaper=session['question_paper'],
            sessionHistory=chat_history
        )
        
        # chatAgent returns {"answer": ..., "question_summary": ...}
        # "question_summary" actually contains the full question paper structure in both direct and plan cases
        answer = result.get("answer")
        result_qp = result.get("question_summary")
        
        session['chat_history'].append({"role": "user", "content": message})
        if answer:
            session['chat_history'].append({"role": "assistant", "content": answer})
            
        updated = False
        if result_qp:
            updated = compare_question_papers(session['question_paper'], result_qp)
            if updated:
                session['question_paper_summary'] = None  # Fix typo: question_Paper_summary -> question_paper_summary
                session['question_paper'] = result_qp
        
        # Determine response type for frontend
        response_type = "mixed"
        if updated and not answer:
            response_type = "qp_update"
        elif answer and not updated:
            response_type = "direct_answer"
            
        response_data = {
            "session_id": session_id,
            "type": response_type,
            "answer": answer,
            "question_paper": session['question_paper'],
            "changes_made": updated
        }
        
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[CHAT ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500


def compare_question_papers(current_qp, new_qp):
    """
    Compare two question papers to detect if any changes were made
    Returns True if differences found, False otherwise
    """
    try:
        if len(current_qp) != len(new_qp):
            return True
        
        for i, (current_co, new_co) in enumerate(zip(current_qp, new_qp)):
            # Compare questions lists
            current_questions = set(current_co.get("questions", []))
            new_questions = set(new_co.get("questions", []))
            
            if current_questions != new_questions:
                return True
        
        return False
    except Exception:
        # If comparison fails, assume changes were made
        return True

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get session state including question paper and chat history
    
    Response:
    {
        "session_id": "task_id",
        "question_paper": [...],
        "chat_history": [...],
        "created_at": timestamp,
        "last_updated": timestamp
    }
    """
    if session_id not in session_store:
        return jsonify({
            "error": "Session not found"
        }), 404
    
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
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "active_tasks": len(active_tasks),
        "completed_tasks": len(task_results),
        "active_sessions": len(session_store)
    }), 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
