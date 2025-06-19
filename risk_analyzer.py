import json
from typing import Dict, Any, List

class RiskAnalyzer:
    def __init__(self):
        self.high_risk_actions = {
            'iam:*', 'iam:CreateRole', 'iam:AttachRolePolicy', 'iam:PutRolePolicy',
            'sts:AssumeRole', 'ec2:*', 'ec2:RunInstances', 'ec2:TerminateInstances',
            's3:*', 's3:DeleteBucket', 's3:PutBucketPolicy', 's3:PutBucketAcl',
            'lambda:*', 'lambda:CreateFunction', 'lambda:UpdateFunctionCode',
            'rds:*', 'rds:DeleteDBInstance', 'rds:CreateDBInstance',
            'cloudformation:*', 'cloudformation:CreateStack', 'cloudformation:DeleteStack'
        }
        
        self.admin_actions = {
            '*', 'iam:*', 'ec2:*', 's3:*', 'lambda:*', 'rds:*', 'cloudformation:*'
        }
        
        self.sensitive_resources = {
            '*', 'arn:aws:iam::*:*', 'arn:aws:s3:::*'
        }
    
    def analyze_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an IAM policy for security risks and provide a risk score."""
        
        risk_score = 0
        issues = []
        recommendations = []
        
        statements = policy.get('Statement', [])
        if not isinstance(statements, list):
            statements = [statements]
        
        for i, statement in enumerate(statements):
            statement_risks = self._analyze_statement(statement, i)
            risk_score += statement_risks['score']
            issues.extend(statement_risks['issues'])
            recommendations.extend(statement_risks['recommendations'])
        
        # Normalize risk score to 0-100 scale
        max_possible_score = len(statements) * 50  # Rough estimate
        normalized_score = min(100, (risk_score / max(max_possible_score, 1)) * 100)
        
        risk_level = self._get_risk_level(normalized_score)
        
        return {
            'risk_score': round(normalized_score, 1),
            'risk_level': risk_level,
            'issues': issues,
            'recommendations': recommendations,
            'summary': self._generate_summary(normalized_score, len(issues))
        }
    
    def _analyze_statement(self, statement: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Analyze a single policy statement."""
        
        score = 0
        issues = []
        recommendations = []
        
        effect = statement.get('Effect', '')
        actions = self._normalize_to_list(statement.get('Action', []))
        resources = self._normalize_to_list(statement.get('Resource', []))
        conditions = statement.get('Condition', {})
        
        # Check for overly broad permissions
        if effect == 'Allow':
            # Check for wildcard actions
            if '*' in actions:
                score += 30
                issues.append(f"Statement {index + 1}: Grants all actions (*) - extremely broad permissions")
                recommendations.append(f"Statement {index + 1}: Specify only the required actions instead of using '*'")
            
            # Check for admin-level actions
            admin_actions_found = [action for action in actions if action in self.admin_actions]
            if admin_actions_found:
                score += 20
                issues.append(f"Statement {index + 1}: Contains administrative actions: {', '.join(admin_actions_found)}")
                recommendations.append(f"Statement {index + 1}: Consider if administrative permissions are truly necessary")
            
            # Check for high-risk actions
            high_risk_found = [action for action in actions if action in self.high_risk_actions]
            if high_risk_found:
                score += 15
                issues.append(f"Statement {index + 1}: Contains high-risk actions: {', '.join(high_risk_found)}")
                recommendations.append(f"Statement {index + 1}: Review if these high-risk actions are necessary")
            
            # Check for wildcard resources
            if '*' in resources:
                score += 25
                issues.append(f"Statement {index + 1}: Grants access to all resources (*)")
                recommendations.append(f"Statement {index + 1}: Specify exact resource ARNs instead of using '*'")
            
            # Check for sensitive resources
            sensitive_found = [res for res in resources if res in self.sensitive_resources]
            if sensitive_found:
                score += 10
                issues.append(f"Statement {index + 1}: Accesses sensitive resources: {', '.join(sensitive_found)}")
            
            # Check for missing conditions
            if not conditions and (admin_actions_found or high_risk_found):
                score += 10
                issues.append(f"Statement {index + 1}: High-privilege actions without conditions")
                recommendations.append(f"Statement {index + 1}: Add conditions like IP restrictions or MFA requirements")
        
        # Check for potential issues with Deny statements
        elif effect == 'Deny':
            if '*' in actions and '*' in resources:
                score += 5
                issues.append(f"Statement {index + 1}: Denies all actions on all resources - may be too restrictive")
        
        return {
            'score': score,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _normalize_to_list(self, value) -> List[str]:
        """Convert string or list to list of strings."""
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list):
            return value
        else:
            return []
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level based on score."""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_summary(self, score: float, issue_count: int) -> str:
        """Generate a summary of the risk analysis."""
        risk_level = self._get_risk_level(score)
        
        if risk_level == "HIGH":
            return f"This policy has a HIGH risk score ({score:.1f}/100) with {issue_count} security concerns. Immediate review and revision recommended."
        elif risk_level == "MEDIUM":
            return f"This policy has a MEDIUM risk score ({score:.1f}/100) with {issue_count} issues. Consider tightening permissions."
        elif risk_level == "LOW":
            return f"This policy has a LOW risk score ({score:.1f}/100) with {issue_count} minor issues. Generally follows good practices."
        else:
            return f"This policy has a MINIMAL risk score ({score:.1f}/100). Follows security best practices well."
