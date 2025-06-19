from flask import Flask, render_template, request, jsonify
import openai
import json
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)

# Initialize our custom classes with lazy loading
policy_gen = None
risk_analyzer = None

def get_policy_generator():
    global policy_gen
    if policy_gen is None:
        from policy_generator import PolicyGenerator
        policy_gen = PolicyGenerator()
    return policy_gen

def get_risk_analyzer():
    global risk_analyzer
    if risk_analyzer is None:
        from risk_analyzer import RiskAnalyzer
        risk_analyzer = RiskAnalyzer()
    return risk_analyzer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-policy', methods=['POST'])
def generate_policy():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Generate the IAM policy
        policy = get_policy_generator().generate_policy(prompt)
        
        # Analyze risks
        risk_analysis = get_risk_analyzer().analyze_policy(policy)
        
        return jsonify({
            'policy': policy,
            'risk_analysis': risk_analysis,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/explain-policy', methods=['POST'])
def explain_policy():
    try:
        data = request.get_json()
        policy = data.get('policy', '')
        
        if not policy:
            return jsonify({'error': 'No policy provided'}), 400
        
        explanation = get_policy_generator().explain_policy(policy)
        
        return jsonify({
            'explanation': explanation,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
