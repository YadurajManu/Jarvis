from flask import Flask, request, jsonify, render_template
import os
import json
from datetime import datetime
from jarvis import JarvisAssistant

app = Flask(__name__)
app.static_folder = 'static'

# Initialize Jarvis with API key in web mode
API_KEY = "AIzaSyADsfm9r5e6Ok18pFXiUmXzOX1_BLuQzPs"
jarvis = JarvisAssistant(API_KEY, web_mode=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def handle_command():
    try:
        data = request.json
        if not data or 'command' not in data:
            return jsonify({'error': 'No command provided'}), 400
            
        command = data['command'].strip()
        if not command:
            return jsonify({'error': 'Empty command'}), 400
            
        # Process the command using Jarvis
        response = jarvis.process_command(command)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error processing command: {e}")
        return jsonify({
            'response': "I apologize, but I encountered an error processing your request.",
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    try:
        workflows = jarvis.get_workflows()
        return jsonify({
            'workflows': workflows,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return jsonify({
            'error': 'Failed to get workflows',
            'status': 'error'
        }), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Workflow name is required'}), 400
            
        name = data['name']
        steps = data.get('steps', [])
        
        workflow = jarvis.create_workflow(steps)
        return jsonify({
            'workflow': workflow,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error creating workflow: {e}")
        return jsonify({
            'error': 'Failed to create workflow',
            'status': 'error'
        }), 500

@app.route('/api/workflows/execute', methods=['POST'])
def execute_workflow():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Workflow name is required'}), 400
            
        name = data['name']
        response = jarvis.execute_workflow(name)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error executing workflow: {e}")
        return jsonify({
            'error': 'Failed to execute workflow',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    # Ensure the static and templates directories exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, port=5000) 