# InkWell AI Frontend

A modern, AI-powered documentation dashboard built with Next.js, React, and TypeScript. This frontend application provides an intuitive interface for generating, editing, and managing technical documentation with AI assistance.

## Features

- **Markdown Editor**: Rich text editing with live preview
- **AI-Powered Documentation**: Generate SRS/SDS documents from code
- **Document Analysis**: Get AI-powered suggestions for improving documentation
- **Project Management**: Organize documents by projects
- **Real-time Collaboration**: Multiple users can collaborate on documents
- **Dark/Light Mode**: Toggle between themes for comfortable reading
- **Responsive Design**: Works on desktop and tablet devices

## Prerequisites

- Node.js 18.0.0 or later
- npm or yarn
- Backend API server (see [backend README](../backend/README.md) for setup)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/inkwell-ai.git
   cd inkwell-ai/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_APP_NAME=InkWell AI
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**
   The application will be available at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── public/            # Static files
├── src/
│   ├── app/           # Next.js app directory
│   ├── components/    # Reusable UI components
│   ├── contexts/      # React contexts
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions
│   ├── styles/        # Global styles
│   └── types/         # TypeScript type definitions
├── .eslintrc.js       # ESLint configuration
├── .gitignore
├── next.config.js     # Next.js configuration
├── package.json
└── tsconfig.json     # TypeScript configuration
```

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the application for production
- `npm start` - Start the production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm test` - Run tests

## Development

### Code Style

This project uses:
- [ESLint](https://eslint.org/) for code linting
- [Prettier](https://prettier.io/) for code formatting
- [TypeScript](https://www.typescriptlang.org/) for type safety

### Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

### Testing

Run the test suite:
```bash
npm test
```

Run tests in watch mode:
```bash
npm test -- --watch
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_APP_NAME` | Application name | `InkWell AI` |

## Deployment

### Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

### Docker

1. Build the Docker image:
   ```bash
   docker build -t inkwell-ai-frontend .
   ```

2. Run the container:
   ```bash
   docker run -p 3000:3000 inkwell-ai-frontend
   ```

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
