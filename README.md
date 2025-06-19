# IAM Policy Generator

A web-based tool that converts natural language descriptions into secure AWS IAM policies using OpenAI's GPT models. The application includes risk analysis and policy explanation features to help ensure security best practices.

## Security Context and Purpose

AWS Identity and Access Management (IAM) policies are critical security components that control access to cloud resources. However, creating secure IAM policies is challenging for several reasons:

### The Problem
- **Complex Syntax**: IAM policies use JSON with specific AWS syntax that's difficult to write correctly
- **Security Risks**: Overly permissive policies can expose organizations to data breaches and unauthorized access
- **Knowledge Gap**: Many developers lack deep understanding of AWS security best practices
- **Time Consuming**: Manual policy creation is slow and error-prone
- **Inconsistency**: Different team members may create policies with varying security standards

### Why This Tool Exists
This IAM Policy Generator addresses these challenges by:

1. **Democratizing Security**: Enables developers without deep AWS security expertise to create secure policies
2. **Reducing Human Error**: Automated generation reduces syntax errors and security misconfigurations
3. **Enforcing Best Practices**: Built-in risk analysis ensures policies follow least-privilege principles
4. **Accelerating Development**: Converts natural language to policies in seconds instead of hours
5. **Educational Value**: Explanations help users understand what policies do and why they're secure
6. **Consistency**: Standardizes policy creation across teams and projects

### Security Benefits
- **Least Privilege by Default**: Policies are generated with minimal necessary permissions
- **Risk Scoring**: Automatic identification of potentially dangerous permissions
- **Security Recommendations**: Actionable advice for improving policy security
- **No AWS Access Required**: Tool operates independently without requiring AWS credentials
- **Audit Trail**: Clear documentation of what each policy does in plain English

## Features

- **Natural Language to IAM Policy**: Convert plain English descriptions into valid AWS IAM policies
- **Risk Analysis**: Automatic security risk scoring and identification of potential issues
- **Policy Explanation**: Get plain English explanations of what IAM policies do
- **Security Best Practices**: Built-in recommendations for improving policy security
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Modern Web Interface**: Responsive design with syntax highlighting and copy functionality

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IAMPolicyGenerator
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

### OpenAI API Key

1. Sign up at [OpenAI](https://platform.openai.com/)
2. Create an API key in your dashboard
3. Add the key to your `.env` file

## Usage

### Basic Usage

1. Enter a natural language description of the permissions you need
2. Click "Generate Policy" to create an IAM policy
3. Review the generated policy and security analysis
4. Use the "Explain" button to get a plain English explanation
5. Copy the policy JSON for use in AWS

### Example Prompts

- "Allow read-only access to S3 bucket 'customer-logs' but block deletion"
- "Allow EC2 instance management but only in us-east-1 region"
- "Allow Lambda function creation and execution with CloudWatch logging"
- "Allow RDS read access but deny database deletion"

### Security Analysis

The tool automatically analyzes generated policies for:

- **Overly broad permissions** (wildcards in actions/resources)
- **High-risk actions** (administrative or destructive operations)
- **Missing conditions** (lack of IP restrictions, MFA requirements)
- **Sensitive resource access** (IAM, root account access)

Risk levels are categorized as:
- **HIGH** (70-100): Immediate review required
- **MEDIUM** (40-69): Consider tightening permissions
- **LOW** (20-39): Minor issues, generally good
- **MINIMAL** (0-19): Follows security best practices

## Architecture

```
├── app.py                 # Flask application entry point
├── policy_generator.py    # OpenAI integration for policy generation
├── risk_analyzer.py       # Security risk analysis engine
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/style.css     # Custom styling
│   └── js/app.js         # Frontend JavaScript
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container setup
└── requirements.txt      # Python dependencies
```

## Security Considerations

- **No AWS Credentials Required**: The tool only generates policies; it doesn't interact with AWS
- **Rate Limiting**: Built-in protection against API abuse
- **Input Validation**: Sanitization of user inputs
- **Secure Defaults**: Policies follow least-privilege principles
- **Risk Analysis**: Automatic identification of security issues

## Development

### Local Development

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key
   ```

3. **Run the development server**
   ```bash
   python app.py
   ```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Code Structure

- **`policy_generator.py`**: Handles OpenAI API integration and policy generation
- **`risk_analyzer.py`**: Analyzes policies for security risks and provides recommendations
- **`app.py`**: Flask web application with API endpoints
- **Frontend**: Modern JavaScript with Bootstrap for responsive design

## API Endpoints

### Generate Policy
```http
POST /generate-policy
Content-Type: application/json

{
  "prompt": "Allow read-only access to S3 bucket 'customer-logs'"
}
```

### Explain Policy
```http
POST /explain-policy
Content-Type: application/json

{
  "policy": { ... }
}
```

### Health Check
```http
GET /health
```

## Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Deployment

For production deployment, consider:

1. **Use HTTPS**: Configure SSL certificates
2. **Environment Security**: Secure your OpenAI API key
3. **Rate Limiting**: Implement additional rate limiting
4. **Monitoring**: Set up logging and monitoring
5. **Backup**: Regular backups of any persistent data

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Disclaimer

This tool uses AI to generate IAM policies and should be used as a starting point only. Always review generated policies carefully before implementing them in production environments. The tool may not cover all security considerations or edge cases.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## Acknowledgments

- OpenAI for providing the GPT models
- AWS for comprehensive IAM documentation
- The open-source community for various libraries and tools used
