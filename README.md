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

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- PostgreSQL 14+
- pnpm 8.x
- Python 3.10+ (for ML components)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/inkwell-ai.git
   cd inkwell-ai
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   pnpm install
   
   # Install frontend dependencies
   cd frontend
   pnpm install
   
   # Install backend dependencies
   cd ../backend
   pnpm install
   ```

3. **Set up environment variables**
   Create `.env` files in both `frontend` and `backend` directories:
   
   ```env
   # frontend/.env
   NEXT_PUBLIC_API_URL=http://localhost:3001
   NEXT_PUBLIC_APP_ENV=development
   ```
   
   ```env
   # backend/.env
   DATABASE_URL="postgresql://user:password@localhost:5432/inkwell_ai"
   NODE_ENV=development
   PORT=3001
   JWT_SECRET=your_jwt_secret_here
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Database Setup**
   ```bash
   cd backend
   pnpm prisma migrate dev
   pnpm prisma db seed
   ```

5. **Running the Application**
   
   In separate terminal windows:
   
   ```bash
   # Start backend
   cd backend
   pnpm dev
   
   # Start frontend
   cd ../frontend
   pnpm dev
   ```

   The application will be available at `http://localhost:3000`

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
