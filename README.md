# InkWell AI: Smarter, Faster, Maintainable Documentation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🚀 Overview

InkWell AI is an intelligent documentation platform that leverages machine learning to transform how developers create, maintain, and interact with technical documentation. As part of the Industry Collaboration Track's "Fix The Docs" initiative, InkWell AI addresses critical challenges in developer productivity and software quality at scale.

## 🎯 Problem Statement

Modern software development faces significant challenges in documentation:

- **Outdated Documentation**: Code evolves faster than documentation
- **Knowledge Silos**: Critical information is scattered across multiple platforms
- **Quality Issues**: Inconsistent formatting, missing context, and technical inaccuracies
- **Search Inefficiency**: Difficulty in finding relevant documentation
- **Maintenance Overhead**: High cost of keeping documentation up-to-date

## ✨ Features

### 🧠 AI-Powered Documentation Assistant
- **Intelligent Code Analysis**: Automatically generates comprehensive documentation for multiple programming languages
- **Smart Suggestions**: AI-powered recommendations for improving documentation quality
- **Real-time Preview**: See documentation updates as you type or upload code
- **Multi-language Support**: Works with Python, JavaScript, TypeScript, HTML, CSS, and more

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

## 🏆 Hackathon Ready

This project is specifically designed to win hackathons with its:
- **Rapid Setup**: Get started in minutes with our easy setup process
- **Modern Tech Stack**: Built with the latest technologies for maximum performance
- **Scalable Architecture**: Ready to handle projects of any size
- **Beautiful UI**: Professional, responsive design that impresses judges

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenAI GPT-4 for documentation generation
- **Authentication**: JWT-based authentication
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

## 🌐 Deployment

### Production Build

```bash
# Build frontend
cd frontend
pnpm build

# Build backend
cd ../backend
pnpm build
```

### Deployment Options

1. **Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

2. **Platform as a Service**
   - Vercel (Frontend)
   - Railway (Backend & Database)
   - Supabase (Alternative to PostgreSQL)

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
