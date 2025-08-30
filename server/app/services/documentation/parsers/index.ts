import * as babel from '@babel/parser';
import * as types from '@babel/types';
import traverse from '@babel/traverse';
import { parse as pythonParse } from 'python-ast';
import { extname } from 'path';
import { DOCUMENTATION_CONFIG } from '../config';

interface CodeElement {
  type: string;
  name: string;
  docstring: string | null;
  code: string;
  startLine: number;
  endLine: number;
  filePath: string;
  params?: Array<{
    name: string;
    type?: string;
    description?: string;
    required: boolean;
  }>;
  returns?: {
    type?: string;
    description?: string;
  };
}

export class CodeParser {
  static async parseFile(filePath: string, content: string): Promise<CodeElement[]> {
    const extension = extname(filePath).toLowerCase();
    
    switch (extension) {
      case '.js':
      case '.jsx':
      case '.ts':
      case '.tsx':
        return this.parseJavaScript(content, filePath);
      case '.py':
        return this.parsePython(content, filePath);
      default:
        console.warn(`Unsupported file extension: ${extension}`);
        return [];
    }
  }

  private static parseJavaScript(content: string, filePath: string): CodeElement[] {
    const elements: CodeElement[] = [];
    
    try {
      const ast = babel.parse(content, {
        sourceType: 'module',
        plugins: [
          'jsx',
          'typescript',
          'classProperties',
          'decorators-legacy',
          'asyncGenerators',
          'dynamicImport',
          'exportDefaultFrom',
          'exportNamespaceFrom',
          'nullishCoalescingOperator',
          'optionalChaining',
          'objectRestSpread',
        ],
      });

      // Extract JSDoc comments and attach them to their respective nodes
      const comments = new Map();
      ast.comments?.forEach(comment => {
        if (comment.type === 'CommentBlock' && comment.value.trim().startsWith('*')) {
          const lines = comment.value.split('\n').map(line => line.trim().replace(/^\*\s?/, ''));
          const node = this.findNodeForComment(ast, comment);
          if (node) {
            comments.set(node, this.parseJSDoc(comment.value));
          }
        }
      });

      // Process function declarations
      traverse(ast, {
        FunctionDeclaration(path) {
          const node = path.node;
          const docstring = comments.get(node) || this.extractInlineComment(node.leadingComments);
          
          elements.push({
            type: 'function',
            name: node.id?.name || 'anonymous',
            docstring: docstring?.description || null,
            code: content.substring(node.start || 0, node.end || 0),
            startLine: node.loc?.start.line || 0,
            endLine: node.loc?.end.line || 0,
            filePath,
            params: docstring?.params || [],
            returns: docstring?.returns,
          });
        },
        
        // Add more node types as needed (ClassDeclaration, VariableDeclarator, etc.)
      });
      
    } catch (error) {
      console.error(`Error parsing JavaScript/TypeScript file ${filePath}:`, error);
    }
    
    return elements;
  }

  private static parsePython(content: string, filePath: string): CodeElement[] {
    const elements: CodeElement[] = [];
    
    try {
      const ast = pythonParse(content);
      
      // Process Python AST and extract functions/classes with docstrings
      // This is a simplified version - in a real app, you'd handle more node types
      
      ast.body?.forEach(node => {
        if (node.type === 'FunctionDef') {
          const docstring = this.extractPythonDocstring(node);
          
          elements.push({
            type: 'function',
            name: node.name,
            docstring: docstring || null,
            code: content.substring(node.start || 0, node.end || 0),
            startLine: node.lineno || 0,
            endLine: node.end_lineno || 0,
            filePath,
            // Parse Python docstring for params and return values
            ...this.parsePythonDocstring(docstring || ''),
          });
        }
      });
      
    } catch (error) {
      console.error(`Error parsing Python file ${filePath}:`, error);
    }
    
    return elements;
  }

  private static extractPythonDocstring(node: any): string | null {
    if (!node.body?.length) return null;
    
    const firstStatement = node.body[0];
    if (firstStatement.type === 'Expr' && 
        firstStatement.value.type === 'Str') {
      return firstStatement.value.s;
    }
    
    return null;
  }

  private static parsePythonDocstring(docstring: string): {
    params?: Array<{name: string; type?: string; description?: string; required: boolean}>;
    returns?: {type?: string; description?: string};
  } {
    if (!docstring) return {};
    
    const result: {
      params?: Array<{name: string; type?: string; description?: string; required: boolean}>;
      returns?: {type?: string; description?: string};
    } = {};
    
    // Simple regex-based parsing of Google-style Python docstrings
    const paramMatches = docstring.matchAll(/Args:\s*\n([\s\S]*?)(?=\n\w+:|$)/g);
    for (const match of paramMatches) {
      const paramsSection = match[1];
      const paramLines = paramsSection.split('\n').filter(Boolean);
      
      result.params = paramLines.map(line => {
        const paramMatch = line.match(/^\s*(\w+)(?::\s*([^\s]+))?\s*:?\s*(.*)/);
        if (paramMatch) {
          return {
            name: paramMatch[1],
            type: paramMatch[2],
            description: paramMatch[3]?.trim(),
            required: true,
          };
        }
        return null;
      }).filter(Boolean) as any;
    }
    
    const returnsMatch = docstring.match(/Returns:\s*\n\s*([^:]+):?\s*([\s\S]*?)(?=\n\w+:|$)/);
    if (returnsMatch) {
      result.returns = {
        type: returnsMatch[1].trim(),
        description: returnsMatch[2].trim(),
      };
    }
    
    return result;
  }

  private static parseJSDoc(comment: string): {
    description: string;
    params: Array<{name: string; type?: string; description?: string; required: boolean}>;
    returns?: {type?: string; description?: string};
  } {
    const result: {
      description: string;
      params: Array<{name: string; type?: string; description?: string; required: boolean}>;
      returns?: {type?: string; description?: string};
    } = {
      description: '',
      params: [],
    };
    
    const lines = comment
      .split('\n')
      .map(line => line.trim().replace(/^\*\s?\/?\s?/, ''))
      .filter(Boolean);
    
    let currentSection: 'description' | 'param' | 'return' | null = 'description';
    
    for (const line of lines) {
      if (line.startsWith('@param')) {
        currentSection = 'param';
        const paramMatch = line.match(/@param\s+\{([^}]*)\}\s+(\w+)(?:\s+-\s+(.*))?/);
        if (paramMatch) {
          result.params.push({
            name: paramMatch[2],
            type: paramMatch[1],
            description: paramMatch[3] || '',
            required: !paramMatch[1]?.includes('='),
          });
        }
      } else if (line.startsWith('@return') || line.startsWith('@returns')) {
        currentSection = 'return';
        const returnMatch = line.match(/@returns?\s*(?:\{([^}]*)\})?\s*(.*)/);
        if (returnMatch) {
          result.returns = {
            type: returnMatch[1] || '',
            description: returnMatch[2] || '',
          };
        }
      } else if (line.startsWith('@')) {
        // Other JSDoc tags - skip for now
        currentSection = null;
      } else if (currentSection === 'description') {
        result.description += (result.description ? '\n' : '') + line;
      } else if (currentSection === 'param' && result.params.length > 0) {
        // Append to the last param's description
        const lastParam = result.params[result.params.length - 1];
        if (lastParam) {
          lastParam.description = (lastParam.description || '') + '\n' + line;
        }
      } else if (currentSection === 'return' && result.returns) {
        // Append to the return description
        result.returns.description = (result.returns.description || '') + '\n' + line;
      }
    }
    
    return result;
  }

  private static extractInlineComment(comments: any[] | null): {description: string} | null {
    if (!comments?.length) return null;
    
    const comment = comments[0];
    if (comment.type === 'CommentLine') {
      return {
        description: comment.value.trim(),
      };
    }
    
    return null;
  }

  private static findNodeForComment(ast: any, comment: any): any {
    // This is a simplified implementation
    // In a real app, you'd need to find the node that immediately follows the comment
    return null;
  }
}
