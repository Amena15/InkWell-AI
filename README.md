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

- **AI-Powered Documentation Assistant**
  - Natural language processing for intelligent documentation generation
  - Automatic code example generation
  - Context-aware suggestions and completions

- **Smart Search & Discovery**
  - Semantic search across documentation
  - Code-aware documentation linking
  - Contextual recommendations

- **Automated Quality Checks**
  - Broken link detection
  - Outdated content identification
  - Style and consistency validations

- **Collaboration Tools**
  - Real-time collaborative editing
  - Version control integration
  - Commenting and review workflows

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI**: Material-UI (MUI) with custom theme
- **State Management**: React Query + Context API
- **Styling**: Emotion (CSS-in-JS)
- **Build Tool**: Vite

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
