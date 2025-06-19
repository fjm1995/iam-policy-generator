import openai
import json
import re
from typing import Dict, Any

class PolicyGenerator:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def generate_policy(self, prompt: str) -> Dict[str, Any]:
        """Generate an IAM policy from a natural language prompt."""
        
        system_prompt = """You are an AWS IAM policy expert. Convert natural language descriptions into valid AWS IAM policies in JSON format.

Rules:
1. Always return valid JSON that follows AWS IAM policy syntax
2. Use least privilege principle - grant only necessary permissions
3. Be specific with resources when possible
4. Include proper conditions when security requirements are mentioned
5. Use appropriate actions for the requested operations

Example input: "Allow read-only access to S3 bucket 'customer-logs' but block deletion"
Example output:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::customer-logs",
                "arn:aws:s3:::customer-logs/*"
            ]
        },
        {
            "Effect": "Deny",
            "Action": [
                "s3:DeleteObject",
                "s3:DeleteBucket"
            ],
            "Resource": [
                "arn:aws:s3:::customer-logs",
                "arn:aws:s3:::customer-logs/*"
            ]
        }
    ]
}

Return ONLY the JSON policy, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            policy_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response if it's wrapped in markdown
            if "```json" in policy_text:
                policy_text = re.search(r'```json\n(.*?)\n```', policy_text, re.DOTALL).group(1)
            elif "```" in policy_text:
                policy_text = re.search(r'```\n(.*?)\n```', policy_text, re.DOTALL).group(1)
            
            # Parse and validate JSON
            policy = json.loads(policy_text)
            
            # Basic validation
            if not self._validate_policy_structure(policy):
                raise ValueError("Generated policy has invalid structure")
            
            return policy
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse generated policy as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate policy: {e}")
    
    def explain_policy(self, policy: Dict[str, Any]) -> str:
        """Explain what an IAM policy does in plain English."""
        
        system_prompt = """You are an AWS IAM policy expert. Explain the given IAM policy in clear, plain English.

Focus on:
1. What actions are allowed or denied
2. Which resources are affected
3. Any conditions that apply
4. Security implications
5. Potential risks or overly permissive permissions

Be concise but thorough."""

        try:
            policy_json = json.dumps(policy, indent=2)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explain this IAM policy:\n\n{policy_json}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise ValueError(f"Failed to explain policy: {e}")
    
    def _validate_policy_structure(self, policy: Dict[str, Any]) -> bool:
        """Basic validation of IAM policy structure."""
        required_fields = ["Version", "Statement"]
        
        if not all(field in policy for field in required_fields):
            return False
        
        if not isinstance(policy["Statement"], list):
            return False
        
        for statement in policy["Statement"]:
            if not isinstance(statement, dict):
                return False
            if "Effect" not in statement or statement["Effect"] not in ["Allow", "Deny"]:
                return False
            if "Action" not in statement and "NotAction" not in statement:
                return False
        
        return True
