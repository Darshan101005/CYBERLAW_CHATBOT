"""
REST API Server for Cyber Law Chatbot
Flask-based API for React.js frontend integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from chatbot_service import CyberLawChatbotService
from complaint_collector import ComplaintCollector  
from file_processor import FileProcessor
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for React.js frontend

# Initialize chatbot service once
chatbot_service = None

def get_chatbot_service():
    """Get or initialize chatbot service"""
    global chatbot_service
    if chatbot_service is None:
        chatbot_service = CyberLawChatbotService()
    return chatbot_service

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Cyber Law Chatbot API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for general queries with optional file upload
    Request: {"message": "user query", "file": {"name": "doc.pdf", "data": "base64", "type": "application/pdf"}}
    Response: {"response": "bot reply", "detected_language": "English", "intent": "general_query"}
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        file_data = data.get('file')
        
        service = get_chatbot_service()
        
        # Handle file processing if file is provided
        file_path = None
        if file_data:
            try:
                import base64
                import tempfile
                import os
                
                # Decode base64 file data
                file_content = base64.b64decode(file_data['data'].split(',')[1])  # Remove data:mime;base64, prefix
                
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                file_name = file_data['name']
                file_path = os.path.join(temp_dir, f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_name}")
                
                # Save file temporarily
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                
                # Process query with file
                response = service.process_query(user_message, file_path)
                
                # Clean up temporary file
                try:
                    os.remove(file_path)
                except:
                    pass
                    
            except Exception as file_error:
                print(f"File processing error: {file_error}")
                # Fall back to regular text processing
                response = service.process_query(user_message)
        else:
            # Process query without file
            response = service.process_query(user_message)
        
        # Get last conversation turn for metadata
        last_turn = service.conversation_history[-1] if service.conversation_history else {}
        
        return jsonify({
            "response": response,
            "detected_language": last_turn.get("detected_language", "English"),
            "intent": "file_analysis" if file_data else "general_query",
            "timestamp": datetime.now().isoformat(),
            "success": True
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            "error": "Failed to process message",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/complaint/start', methods=['POST'])
def start_complaint():
    """
    Start complaint collection process
    Request: {"initial_complaint": "I want to report fraud"}
    Response: {"complaint_id": "CYBER_...", "message": "...", "next_question": {...}}
    """
    try:
        data = request.get_json()
        if not data or 'initial_complaint' not in data:
            return jsonify({"error": "Initial complaint text is required"}), 400
        
        collector = ComplaintCollector()
        result = collector.start_complaint_collection(data['initial_complaint'])
        
        return jsonify({
            "complaint_id": result["complaint_id"],
            "message": result["message"],
            "next_question": result["next_question"],
            "progress": result["progress"],
            "success": True
        })
        
    except Exception as e:
        print(f"Complaint start error: {e}")
        return jsonify({
            "error": "Failed to start complaint collection",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/complaint/answer', methods=['POST'])
def answer_complaint():
    """
    Continue complaint collection with user answer
    Request: {"complaint_id": "CYBER_...", "answer": "user answer"}
    Response: {"message": "...", "next_question": {...}, "completed": false}
    """
    try:
        data = request.get_json()
        if not data or 'complaint_id' not in data or 'answer' not in data:
            return jsonify({"error": "Complaint ID and answer are required"}), 400
        
        collector = ComplaintCollector()
        result = collector.process_answer(data['complaint_id'], data['answer'])
        
        if 'error' in result:
            return jsonify({"error": result['error'], "success": False}), 400
        
        is_completed = result.get("status") == "completed"
        
        response = {
            "message": result["message"],
            "completed": is_completed,
            "success": True
        }
        
        if not is_completed:
            response["next_question"] = result["next_question"]
            response["progress"] = result["progress"]
            response["completion"] = result["completion"]
        else:
            response["file_path"] = result.get("file_path")
            response["summary"] = result.get("summary")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Complaint answer error: {e}")
        return jsonify({
            "error": "Failed to process answer",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/file/analyze', methods=['POST'])
def analyze_file():
    """
    Analyze uploaded file for legal issues
    Request: multipart/form-data with 'file' field
    Response: {"analysis": {...}, "legal_advice": "...", "success": true}
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        
        try:
            # Process file
            processor = FileProcessor()
            result = processor.process_uploaded_file(temp_file.name, file.filename)
            
            if not result.get("success"):
                return jsonify({
                    "error": result.get("error", "File processing failed"),
                    "success": False
                }), 400
            
            # Get analysis summary
            summary = processor.get_file_analysis_summary(result)
            
            # Generate legal advice
            service = get_chatbot_service()
            legal_advice = service.generate_file_based_legal_advice(result, f"Analyze file: {file.filename}")
            
            return jsonify({
                "filename": file.filename,
                "analysis": result["analysis"],
                "summary": summary,
                "legal_advice": legal_advice,
                "processed_id": result["processed_id"],
                "file_info": result["file_info"],
                "success": True
            })
            
        finally:
            # Clean up temp file
            os.unlink(temp_file.name)
        
    except Exception as e:
        print(f"File analysis error: {e}")
        return jsonify({
            "error": "Failed to analyze file",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/complaint/<complaint_id>/download', methods=['GET'])
def download_complaint(complaint_id):
    """
    Download final complaint file
    Response: JSON file download
    """
    try:
        file_path = f"CYBERLAW_CHATBOT/complaints/FINAL_{complaint_id}.json"
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Complaint file not found"}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"complaint_{complaint_id}.json",
            mimetype='application/json'
        )
        
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({
            "error": "Failed to download complaint",
            "details": str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_conversation_history():
    """
    Get conversation history for current session
    Response: {"history": [...], "count": 5}
    """
    try:
        service = get_chatbot_service()
        
        return jsonify({
            "history": service.conversation_history,
            "count": len(service.conversation_history),
            "max_turns": service.max_history_turns,
            "success": True
        })
        
    except Exception as e:
        print(f"History error: {e}")
        return jsonify({
            "error": "Failed to get conversation history",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_session():
    """
    Clear conversation history and reset session
    Response: {"message": "Session cleared", "success": true}
    """
    try:
        global chatbot_service
        chatbot_service = None  # Reset service
        
        return jsonify({
            "message": "Session cleared successfully",
            "success": True
        })
        
    except Exception as e:
        print(f"Clear error: {e}")
        return jsonify({
            "error": "Failed to clear session",
            "details": str(e),
            "success": False
        }), 500

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    docs = {
        "title": "Cyber Law Chatbot API",
        "version": "1.0.0",
        "description": "REST API for cyber law assistance with complaint collection and file analysis",
        "endpoints": {
            "GET /health": "Health check",
            "POST /api/chat": "General chat queries",
            "POST /api/complaint/start": "Start complaint collection",
            "POST /api/complaint/answer": "Continue complaint collection",
            "POST /api/file/analyze": "Analyze uploaded files",
            "GET /api/complaint/<id>/download": "Download complaint file",
            "GET /api/history": "Get conversation history",
            "POST /api/clear": "Clear session data"
        },
        "features": [
            "Multilingual support (Hindi, Tamil, English, etc.)",
            "Color-coded legal act categorization",
            "Interactive complaint collection (15 questions)",
            "File analysis (text, PDF, JSON)",
            "Conversation memory (6 turns)",
            "JSON complaint export"
        ]
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    print("🚀 Starting Cyber Law Chatbot API Server...")
    print("📍 API Documentation: http://localhost:5000/api/docs")
    print("🔍 Health Check: http://localhost:5000/health")
    print("💬 Chat Endpoint: POST http://localhost:5000/api/chat")
    
    app.run(host='0.0.0.0', port=5000, debug=True)