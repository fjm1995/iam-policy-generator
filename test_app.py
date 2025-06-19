import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_page(client):
    """Test the main page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'IAM Policy Generator' in response.data

@patch('policy_generator.PolicyGenerator.generate_policy')
@patch('risk_analyzer.RiskAnalyzer.analyze_policy')
def test_generate_policy_success(mock_analyze, mock_generate, client):
    """Test successful policy generation."""
    # Mock the policy generation
    mock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::test-bucket/*"]
            }
        ]
    }
    mock_generate.return_value = mock_policy
    
    # Mock the risk analysis
    mock_risk = {
        "risk_score": 25.0,
        "risk_level": "LOW",
        "issues": [],
        "recommendations": [],
        "summary": "This policy has a LOW risk score."
    }
    mock_analyze.return_value = mock_risk
    
    # Test the endpoint
    response = client.post('/generate-policy', 
                          json={'prompt': 'Allow read access to S3 bucket test-bucket'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['policy'] == mock_policy
    assert data['risk_analysis'] == mock_risk

def test_generate_policy_no_prompt(client):
    """Test policy generation with no prompt."""
    response = client.post('/generate-policy', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('policy_generator.PolicyGenerator.explain_policy')
def test_explain_policy_success(mock_explain, client):
    """Test successful policy explanation."""
    mock_explanation = "This policy allows read access to S3 objects."
    mock_explain.return_value = mock_explanation
    
    test_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::test-bucket/*"]
            }
        ]
    }
    
    response = client.post('/explain-policy', json={'policy': test_policy})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['explanation'] == mock_explanation

def test_explain_policy_no_policy(client):
    """Test policy explanation with no policy."""
    response = client.post('/explain-policy', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

if __name__ == '__main__':
    pytest.main([__file__])
