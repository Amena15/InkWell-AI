import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import { SentenceTransformer } from 'sentence-transformers-node';
import { writeFileSync, readFileSync } from 'fs';
import { join } from 'path';

interface CodeElement {
  type: 'function' | 'class' | 'interface' | 'variable';
  name: string;
  docstring: string | null;
  code: string;
  startLine: number;
  endLine: number;
  filePath: string;
}

interface DocumentationIssue {
  element: CodeElement;
  issueType: 'missing' | 'inconsistent' | 'outdated';
  confidence: number;
  suggestion?: string;
}

export class DocumentationAnalyzer {
  private model: any;
  private issues: DocumentationIssue[] = [];
  private readonly SUPPORTED_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx', '.py'];

  constructor() {
    // Initialize the sentence transformer model
    this.initializeModel();
  }

  private async initializeModel() {
    this.model = await SentenceTransformer.load('all-MiniLM-L6-v2');
  }

  public async analyzeCodebase(rootDir: string): Promise<DocumentationIssue[]> {
    const files = this.findCodeFiles(rootDir);
    
    for (const file of files) {
      try {
        const code = readFileSync(file, 'utf-8');
        const elements = this.extractCodeElements(code, file);
        await this.checkDocumentation(elements);
      } catch (error) {
        console.error(`Error analyzing ${file}:`, error);
      }
    }

    return this.issues;
  }

  private findCodeFiles(dir: string): string[] {
    // Implementation to recursively find code files
    // This is a simplified version - in a real app, you'd use fs.readdirSync recursively
    return [];
  }

  private extractCodeElements(code: string, filePath: string): CodeElement[] {
    const elements: CodeElement[] = [];
    
    try {
      const ast = parse(code, {
        sourceType: 'module',
        plugins: ['typescript', 'jsx', 'classProperties']
      });

      traverse(ast, {
        FunctionDeclaration(path) {
          const docstring = path.node.leadingComments?.find(c => 
            c.type === 'CommentBlock' && c.value.trim().startsWith('*')
          )?.value;

          elements.push({
            type: 'function',
            name: path.node.id?.name || 'anonymous',
            docstring: docstring || null,
            code: code.substring(path.node.start || 0, path.node.end || 0),
            startLine: path.node.loc?.start.line || 0,
            endLine: path.node.loc?.end.line || 0,
            filePath
          });
        },
        // Add more visitors for classes, interfaces, etc.
      });
    } catch (error) {
      console.error('Error parsing code:', error);
    }

    return elements;
  }

  private async checkDocumentation(elements: CodeElement[]): Promise<void> {
    for (const element of elements) {
      if (!element.docstring) {
        this.issues.push({
          element,
          issueType: 'missing',
          confidence: 1.0,
          suggestion: this.generateDocumentationSuggestion(element)
        });
        continue;
      }

      // Check documentation quality using semantic similarity
      const similarity = await this.checkDocumentationQuality(element);
      if (similarity < 0.7) { // Threshold for documentation quality
        this.issues.push({
          element,
          issueType: 'inconsistent',
          confidence: 1 - similarity,
          suggestion: this.generateDocumentationSuggestion(element)
        });
      }
    }
  }

  private async checkDocumentationQuality(element: CodeElement): Promise<number> {
    if (!element.docstring) return 0;
    
    // Get embeddings for code and documentation
    const codeEmbedding = await this.model.encode(element.code);
    const docEmbedding = await this.model.encode(element.docstring);
    
    // Calculate cosine similarity
    return this.cosineSimilarity(codeEmbedding, docEmbedding);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    return dotProduct / (magnitudeA * magnitudeB);
  }

  private generateDocumentationSuggestion(element: CodeElement): string {
    // This is a simplified version - in a real app, you'd use more sophisticated logic
    return `/**
 * ${element.name} - Add description here
 * 
 * @param {type} paramName - parameter description
 * @returns {type} return value description
 */`;
  }

  public generateReport(outputPath: string): void {
    const report = {
      timestamp: new Date().toISOString(),
      issues: this.issues,
      summary: {
        totalIssues: this.issues.length,
        missingDocs: this.issues.filter(i => i.issueType === 'missing').length,
        inconsistentDocs: this.issues.filter(i => i.issueType === 'inconsistent').length
      }
    };

    writeFileSync(outputPath, JSON.stringify(report, null, 2));
  }
}
