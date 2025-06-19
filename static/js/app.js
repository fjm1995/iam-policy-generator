// IAM Policy Generator Frontend JavaScript

class PolicyGenerator {
    constructor() {
        this.currentPolicy = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('policyForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generatePolicy();
        });

        // Example prompt clicks
        document.querySelectorAll('.example-prompt').forEach(button => {
            button.addEventListener('click', (e) => {
                const prompt = e.target.getAttribute('data-prompt');
                document.getElementById('promptInput').value = prompt;
            });
        });

        // Copy button
        document.getElementById('copyBtn').addEventListener('click', () => {
            this.copyPolicy();
        });

        // Explain button
        document.getElementById('explainBtn').addEventListener('click', () => {
            this.explainPolicy();
        });

        // New Policy button
        document.getElementById('newPolicyBtn').addEventListener('click', () => {
            this.resetForm();
        });
    }

    async generatePolicy() {
        const prompt = document.getElementById('promptInput').value.trim();
        
        if (!prompt) {
            this.showError('Please enter a prompt');
            return;
        }

        this.setLoadingState(true);
        this.hideError();
        this.hideExplanation();

        try {
            const response = await fetch('/generate-policy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const data = await response.json();

            if (data.success) {
                this.currentPolicy = data.policy;
                this.displayPolicy(data.policy);
                this.displayRiskAnalysis(data.risk_analysis);
                this.showOutput();
            } else {
                this.showError(data.error || 'Failed to generate policy');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    async explainPolicy() {
        if (!this.currentPolicy) {
            this.showError('No policy to explain');
            return;
        }

        this.setLoadingState(true, 'explainBtn');

        try {
            const response = await fetch('/explain-policy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ policy: this.currentPolicy })
            });

            const data = await response.json();

            if (data.success) {
                this.displayExplanation(data.explanation);
            } else {
                this.showError(data.error || 'Failed to explain policy');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.setLoadingState(false, 'explainBtn');
        }
    }

    displayPolicy(policy) {
        const policyOutput = document.getElementById('policyOutput');
        policyOutput.textContent = JSON.stringify(policy, null, 2);
        
        // Trigger syntax highlighting
        if (window.Prism) {
            Prism.highlightElement(policyOutput);
        }
    }

    displayRiskAnalysis(riskAnalysis) {
        const riskContent = document.getElementById('riskContent');
        
        const riskLevelClass = riskAnalysis.risk_level.toLowerCase();
        
        let html = `
            <div class="d-flex align-items-center mb-3">
                <div class="risk-score risk-${riskLevelClass}">${riskAnalysis.risk_score}/100</div>
                <span class="risk-badge ${riskLevelClass} ms-2">${riskAnalysis.risk_level} RISK</span>
            </div>
            <p class="mb-3">${riskAnalysis.summary}</p>
        `;

        if (riskAnalysis.issues && riskAnalysis.issues.length > 0) {
            html += `
                <div class="mb-3">
                    <h6>Security Issues:</h6>
                    ${riskAnalysis.issues.map(issue => `
                        <div class="issue-item">${issue}</div>
                    `).join('')}
                </div>
            `;
        }

        if (riskAnalysis.recommendations && riskAnalysis.recommendations.length > 0) {
            html += `
                <div class="mb-3">
                    <h6>Recommendations:</h6>
                    ${riskAnalysis.recommendations.map(rec => `
                        <div class="recommendation-item">${rec}</div>
                    `).join('')}
                </div>
            `;
        }

        riskContent.innerHTML = html;
    }

    displayExplanation(explanation) {
        const explanationContent = document.getElementById('explanationContent');
        explanationContent.textContent = explanation;
        
        const explanationSection = document.getElementById('explanationSection');
        explanationSection.classList.remove('d-none');
        explanationSection.classList.add('fade-in');
    }

    copyPolicy() {
        if (!this.currentPolicy) {
            this.showError('No policy to copy');
            return;
        }

        const policyText = JSON.stringify(this.currentPolicy, null, 2);
        
        navigator.clipboard.writeText(policyText).then(() => {
            const copyBtn = document.getElementById('copyBtn');
            const originalText = copyBtn.innerHTML;
            
            copyBtn.innerHTML = 'Copied!';
            copyBtn.classList.add('copy-success');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('copy-success');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            this.showError('Failed to copy to clipboard');
        });
    }

    showOutput() {
        document.getElementById('placeholder').classList.add('d-none');
        document.getElementById('outputSection').classList.remove('d-none');
        document.getElementById('outputSection').classList.add('fade-in');
        document.getElementById('copyBtn').style.display = 'inline-block';
        document.getElementById('explainBtn').style.display = 'inline-block';
        document.getElementById('newPolicyBtn').style.display = 'inline-block';
    }

    hideExplanation() {
        document.getElementById('explanationSection').classList.add('d-none');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('d-none');
        errorSection.classList.add('fade-in');
        
        // Hide other sections
        document.getElementById('outputSection').classList.add('d-none');
        document.getElementById('placeholder').classList.remove('d-none');
    }

    hideError() {
        document.getElementById('errorSection').classList.add('d-none');
    }

    resetForm() {
        // Clear the form
        document.getElementById('promptInput').value = '';
        
        // Reset the interface
        this.currentPolicy = null;
        document.getElementById('outputSection').classList.add('d-none');
        document.getElementById('placeholder').classList.remove('d-none');
        document.getElementById('copyBtn').style.display = 'none';
        document.getElementById('explainBtn').style.display = 'none';
        document.getElementById('newPolicyBtn').style.display = 'none';
        this.hideError();
        this.hideExplanation();
        
        // Focus back on the input
        document.getElementById('promptInput').focus();
    }

    setLoadingState(loading, buttonId = 'generateBtn') {
        const button = document.getElementById(buttonId);
        const spinner = document.getElementById('loadingSpinner');
        
        if (loading) {
            button.disabled = true;
            if (buttonId === 'generateBtn') {
                spinner.classList.remove('d-none');
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
            } else {
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Explaining...';
            }
            document.body.classList.add('loading');
        } else {
            button.disabled = false;
            if (buttonId === 'generateBtn') {
                spinner.classList.add('d-none');
                button.innerHTML = 'Generate Policy';
            } else {
                button.innerHTML = 'Explain';
            }
            document.body.classList.remove('loading');
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PolicyGenerator();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
    // Auto-resize textarea
    const textarea = document.getElementById('promptInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to generate policy
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('policyForm').dispatchEvent(new Event('submit'));
        }
    });

    // Add tooltips for better UX
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (window.bootstrap) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
