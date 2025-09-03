# InkWell AI: Intelligent Documentation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🚀 Overview

InkWell AI is an intelligent documentation platform that leverages advanced machine learning to transform how development teams create, maintain, and interact with technical documentation. Our platform addresses critical challenges in developer productivity and software quality at scale, enabling teams to focus on building great software.

## 🎯 Key Challenges in Documentation

Modern development teams face significant documentation challenges:

- **Outdated Documentation**: Code evolves faster than documentation
- **Knowledge Silos**: Critical information scattered across multiple platforms
- **Quality Inconsistencies**: Varying formats, missing context, and technical inaccuracies
- **Inefficient Discovery**: Difficulty in finding relevant documentation
- **High Maintenance**: Significant effort required to keep documentation current

## ✨ Features

### 🧠 AI-Powered Documentation
- **Automated Code Analysis**: Generate comprehensive documentation across multiple programming languages
- **Quality Enhancement**: AI-driven suggestions for improving documentation clarity and completeness
- **Real-time Preview**: Instant visualization of documentation as you write or update code
- **Multi-language Support**: Native support for Python, JavaScript, TypeScript, HTML, CSS, and more

### 🔍 Smart Search & Discovery
- **Semantic Search**: Find relevant documentation using natural language queries
- **Code-Aware Linking**: Automatic linking between related code and documentation
- **Contextual Recommendations**: Intelligent suggestions based on your current context

### 🛠️ Developer Experience
- **Seamless Integration**: Works with your existing codebase and documentation
- **Version Control Ready**: Tracks documentation changes alongside your code
- **Customizable Templates**: Create and use templates for consistent documentation

### 🤖 AI/ML Capabilities
- **Code Understanding**: Deep analysis of code structure and relationships
- **Documentation Generation**: Creates clear, concise, and well-structured documentation
- **Quality Assurance**: Identifies potential issues and suggests improvements

- **API**: RESTful API design with OpenAPI documentation

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI**: Tailwind CSS with custom components
- **State Management**: React Query + Context API
- **Build Tool**: Vite
- **Code Editor**: Monaco Editor for code input

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Testing**: Pytest (backend), Jest + React Testing Library (frontend)

### Backend
- **Runtime**: Node.js with TypeScript
- **API**: Fastify REST API
- **Database**: PostgreSQL with Prisma ORM
- **Search**: Meilisearch
- **AI/ML**: Integration with OpenAI's GPT models

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ & pnpm 8.x
- Python 3.10+
- SQLite (included with most systems)

### Setup (5 minutes)

1. **Clone and install**
   ```bash
   git clone https://github.com/Amena15/InkWell-AI.git
   cd InkWell-AI
   
   # Install frontend deps
   cd frontend && pnpm install
   
   # Install backend deps
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Create `.env` in the backend folder:
   ```env
   DATABASE_URL=sqlite:///./inkwell.db
   SECRET_KEY=your-secret-key-here
   OPENAI_API_KEY=your-openai-api-key
   ```

3. **Run the application**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload
   
   # Terminal 2: Frontend
   cd ../frontend
   pnpm dev
   ```
   
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

### First Time Setup
1. Open the frontend in your browser
2. Sign up for a new account
3. Start documenting your code!

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the Industry Collaboration Track: Fix The Docs
- Special thanks to our mentors and contributors
- Powered by OpenAI and the open-source community
