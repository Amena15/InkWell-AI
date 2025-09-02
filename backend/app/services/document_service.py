import os
import re
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
import openai
from openai import OpenAI
import difflib
import uuid
from dataclasses import dataclass, field
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class DocumentVersion:
    content: str
    author: str
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    comments: List[Dict] = field(default_factory=list)

@dataclass
class Comment:
    content: str
    author: str
    comment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    replies: List[Dict] = field(default_factory=list)

class DocumentCollaboration:
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.versions: List[DocumentVersion] = []
        self.collaborators: Set[str] = set()
        self.pending_suggestions: List[Dict] = []

    def add_version(self, content: str, author: str, message: str = "") -> DocumentVersion:
        version = DocumentVersion(content, author, message=message)
        self.versions.append(version)
        return version

    def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        return next((v for v in self.versions if v.version_id == version_id), None)

    def get_version_diff(self, old_version_id: str, new_version_id: str) -> Dict[str, Any]:
        old_version = self.get_version(old_version_id)
        new_version = self.get_version(new_version_id)
        
        if not old_version or not new_version:
            return {"error": "One or both versions not found"}
            
        diff = difflib.unified_diff(
            old_version.content.splitlines(keepends=True),
            new_version.content.splitlines(keepends=True),
            fromfile=f"version_{old_version_id[:8]}",
            tofile=f"version_{new_version_id[:8]}",
            fromfiledate=old_version.timestamp.isoformat(),
            tofiledate=new_version.timestamp.isoformat(),
            lineterm=''
        )
        
        return {
            "old_version": old_version_id,
            "new_version": new_version_id,
            "diff": '\n'.join(diff),
            "changes": self._calculate_changes(old_version.content, new_version.content)
        }

    def _calculate_changes(self, old_content: str, new_content: str) -> Dict[str, int]:
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        diff = difflib.SequenceMatcher(None, old_lines, new_lines)
        
        return {
            "added": sum(size for op, i1, i2, j1, j2 in diff.get_opcodes() if op == 'insert'),
            "removed": sum(size for op, i1, i2, j1, j2 in diff.get_opcodes() if op == 'delete'),
            "modified": sum(1 for op, i1, i2, j1, j2 in diff.get_opcodes() if op == 'replace')
        }

    def add_comment(self, version_id: str, content: str, author: str) -> Optional[Comment]:
        version = self.get_version(version_id)
        if version:
            comment = Comment(content, author)
            version.comments.append({
                "comment_id": comment.comment_id,
                "content": comment.content,
                "author": comment.author,
                "timestamp": comment.timestamp.isoformat(),
                "resolved": comment.resolved,
                "replies": []
            })
            return comment
        return None

class DocumentService:
    def __init__(self):
        self.supported_formats = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.txt': 'text',
            '.json': 'json'
        }
        self.collaboration_sessions: Dict[str, DocumentCollaboration] = {}
        
        # Initialize code analyzers
        self.analyzers = {
            '.py': self._analyze_python_code,
            '.js': self._analyze_javascript_code,
            '.ts': self._analyze_typescript_code
        }
        
    # Version History Methods
    def create_document_version(self, document_id: str, content: str, author: str, message: str = "") -> Dict[str, Any]:
        """Create a new version of a document."""
        if document_id not in self.collaboration_sessions:
            self.collaboration_sessions[document_id] = DocumentCollaboration(document_id)
            
        collaboration = self.collaboration_sessions[document_id]
        version = collaboration.add_version(content, author, message)
        
        return {
            "document_id": document_id,
            "version_id": version.version_id,
            "timestamp": version.timestamp.isoformat(),
            "author": version.author,
            "message": version.message
        }
    
    def get_document_versions(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a document."""
        if document_id not in self.collaboration_sessions:
            return []
            
        collaboration = self.collaboration_sessions[document_id]
        return [{
            "version_id": v.version_id,
            "timestamp": v.timestamp.isoformat(),
            "author": v.author,
            "message": v.message,
            "content_length": len(v.content)
        } for v in collaboration.versions]
    
    def get_version_diff(self, document_id: str, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Get diff between two versions of a document."""
        if document_id not in self.collaboration_sessions:
            return {"error": "Document not found"}
            
        return self.collaboration_sessions[document_id].get_version_diff(version1_id, version2_id)
    
    # Collaboration Methods
    def add_comment_to_version(self, document_id: str, version_id: str, content: str, author: str) -> Optional[Dict]:
        """Add a comment to a specific version of a document."""
        if document_id not in self.collaboration_sessions:
            return None
            
        collaboration = self.collaboration_sessions[document_id]
        comment = collaboration.add_comment(version_id, content, author)
        
        if comment:
            return {
                "comment_id": comment.comment_id,
                "content": comment.content,
                "author": comment.author,
                "timestamp": comment.timestamp.isoformat(),
                "resolved": comment.resolved
            }
        return None
    
    def get_version_comments(self, document_id: str, version_id: str) -> List[Dict]:
        """Get all comments for a specific version."""
        if document_id not in self.collaboration_sessions:
            return []
            
        collaboration = self.collaboration_sessions[document_id]
        version = collaboration.get_version(version_id)
        
        if not version:
            return []
            
        return [{
            "comment_id": c["comment_id"],
            "content": c["content"],
            "author": c["author"],
            "timestamp": c["timestamp"],
            "resolved": c["resolved"]
        } for c in version.comments]
    
    def resolve_comment(self, document_id: str, version_id: str, comment_id: str, author: str) -> bool:
        """Mark a comment as resolved."""
        if document_id not in self.collaboration_sessions:
            return False
            
        collaboration = self.collaboration_sessions[document_id]
        version = collaboration.get_version(version_id)
        
        if not version:
            return False
            
        for comment in version.comments:
            if comment["comment_id"] == comment_id:
                comment["resolved"] = True
                comment["resolved_by"] = author
                comment["resolved_at"] = datetime.utcnow().isoformat()
                return True
                
        return False
    
    def add_collaborator(self, document_id: str, user_id: str) -> bool:
        """Add a collaborator to the document."""
        if document_id not in self.collaboration_sessions:
            return False
            
        return self.collaboration_sessions[document_id].add_collaborator(user_id)
    
    def get_collaborators(self, document_id: str) -> List[str]:
        """Get all collaborators for a document."""
        if document_id not in self.collaboration_sessions:
            return []
            
        return list(self.collaboration_sessions[document_id].collaborators)
    
    def get_latest_version(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a document."""
        if document_id not in self.collaboration_sessions or not self.collaboration_sessions[document_id].versions:
            return None
            
        version = self.collaboration_sessions[document_id].versions[-1]
        return {
            "document_id": document_id,
            "version_id": version.version_id,
            "content": version.content,
            "author": version.author,
            "timestamp": version.timestamp.isoformat(),
            "message": version.message
        }
        
        # Documentation quality metrics configuration
        self.metrics_config = {
            'coverage_weight': 0.4,
            'readability_weight': 0.3,
            'consistency_weight': 0.3,
            'min_docstring_length': 20,
            'target_readability_score': 60  # 0-100 scale
        }
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.documentation_standards = {
            'python': {
                'function': {
                    'required': ['description', 'parameters', 'returns', 'raises'],
                    'template': """{function_name}
        
        {description}
        
        Args:
            {parameters}
            
        Returns:
            {returns}
            
        Raises:
            {raises}"""
                },
                'class': {
                    'required': ['description', 'attributes', 'methods'],
                    'template': """{class_name}
        
        {description}
        
        Attributes:
            {attributes}
            
        Methods:
            {methods}"""
                }
            },
            'javascript': {
                'function': {
                    'required': ['description', 'params', 'returns', 'throws'],
                    'template': """/**
 * {description}
 * 
 * @param {{{params}}}
 * @returns {{{returns}}}
 * @throws {{{throws}}}
 */"""
                },
                'class': {
                    'required': ['description', 'properties', 'methods'],
                    'template': """/**
 * {description}
 * 
 * @class {class_name}
 * @property {{{properties}}}
 * 
 * @method {methods}
 */"""
                }
            }
        }

    async def process_document(self, file_path: str, previous_version: str = None) -> Dict[str, Any]:
        """
        Process a document to generate and analyze its documentation.
        
        Args:
            file_path: Path to the file to process
            previous_version: Optional previous version of the documentation for diffing
            
        Returns:
            Dict containing processed documentation and analysis results
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Analyze code structure using appropriate analyzer
            code_structure = self._analyze_code_structure(content, file_extension)
            
            # Generate documentation with AI assistance
            documentation = await self._generate_documentation(
                content=content,
                file_extension=file_extension,
                code_structure=code_structure,
                previous_version=previous_version
            )
            
            # Analyze documentation quality
            quality_metrics = self._analyze_documentation_quality(
                content=content,
                documentation=documentation,
                file_extension=file_extension,
                code_structure=code_structure
            )
            
            # Generate diff if previous version exists
            diff = None
            if previous_version:
                diff = self._generate_diff(previous_version, documentation)
            
            # Extract metadata and generate version hash
            metadata = self._extract_metadata(content, file_extension)
            version_hash = self._generate_version_hash(content)
            
            # Calculate overall documentation score
            doc_score = self._calculate_overall_score(quality_metrics)
            
            return {
                "file_path": file_path,
                "documentation": documentation,
                "metadata": metadata,
                "code_structure": code_structure,
                "quality_metrics": {
                    **quality_metrics,
                    "overall_score": doc_score,
                    "grade": self._score_to_grade(doc_score)
                },
                "diff": diff,
                "version_hash": version_hash,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            raise Exception(f"Error processing document: {str(e)}")

    async def _generate_documentation(self, content: str, file_extension: str, 
                                    code_structure: Dict, previous_version: str = None) -> str:
        """Generate documentation using AI with enhanced context."""
        try:
            # Check if OpenAI API key is available
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
                # Fallback documentation when no API key is available
                return self._generate_fallback_documentation(content, file_extension, code_structure)
                
            messages = [
                {
                    "role": "system",
                    "content": """You are an AI documentation assistant. Generate comprehensive documentation 
                    for the provided code. Include function signatures, parameters, return types, 
                    and examples where appropriate."""
                },
                {
                    "role": "user",
                    "content": f"""
                    Please generate documentation for the following {file_extension} code:
                    
                    File content:
                    {content}
                    
                    Code structure analysis:
                    {json.dumps(code_structure, indent=2)}
                    
                    Previous version (if available):
                    {previous_version or 'No previous version available'}
                    
                    Please include:
                    1. File-level documentation
                    2. Function/method documentation
                    3. Class documentation (if applicable)
                    4. Examples (where helpful)
                    5. Any warnings or important notes
                    """
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Process the response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return ""
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return f"Error generating documentation: {str(e)}"
        except SyntaxError as e:
            return {
                'language': 'python',
                'error': f'Syntax error: {str(e)}',
                'line': e.lineno,
                'offset': e.offset
            }

    def _analyze_code_structure(self, content: str, file_extension: str) -> Dict:
        """
        Analyze code structure based on file type.
        
        Args:
            content: Source code content
            file_extension: File extension to determine the analyzer
            
        Returns:
            Dict containing analyzed code structure
        """
        analyzer = self.analyzers.get(file_extension)
        if analyzer:
            try:
                return analyzer(content)
            except Exception as e:
                logger.warning(f"Error analyzing {file_extension} code: {str(e)}")
                return {
                    "file_type": self.supported_formats[file_extension],
                    "error": str(e)
                }
        return {
            "file_type": self.supported_formats[file_extension],
            "warning": "No specific analyzer available for this file type"
        }

    def _analyze_documentation_quality(self, content: str, documentation: str, 
                                      file_extension: str, code_structure: Dict) -> Dict[str, Any]:
        """Analyze documentation quality and completeness."""
        metrics = {
            'completeness_score': 0,
            'coverage_score': 0,
            'readability_score': 0,
            'issues': [],
            'suggestions': []
        }
        
        # Calculate documentation coverage
        total_elements = len(code_structure.get('functions', [])) + len(code_structure.get('classes', []))
        documented_elements = sum(1 for f in code_structure.get('functions', []) if f.get('has_docstring'))
        documented_elements += sum(1 for c in code_structure.get('classes', []) if c.get('has_docstring'))
        
        metrics['coverage_score'] = (documented_elements / total_elements * 100) if total_elements > 0 else 100
        
        # Check for required sections based on language standards
        lang = self.supported_formats[file_extension]
        if lang in self.documentation_standards:
            standards = self.documentation_standards[lang]
            
            for func in code_structure.get('functions', []):
                if func.get('has_docstring'):
                    # Check if all required sections are present
                    doc = func.get('docstring', '')
                    missing_sections = []
                    
                    for section in standards['function']['required']:
                        if f'{section}:' not in doc.lower():
                            missing_sections.append(section)
                    
                    if missing_sections:
                        metrics['issues'].append({
                            'type': 'incomplete_documentation',
                            'element': f"{func['name']}()",
                            'message': f"Missing documentation sections: {', '.join(missing_sections)}",
                            'severity': 'warning'
                        })
        
        # Calculate readability score (simplified)
        doc_length = len(documentation)
        word_count = len(documentation.split())
        avg_word_length = sum(len(word) for word in documentation.split()) / word_count if word_count > 0 else 0
        
        # Simple readability score (higher is better)
        metrics['readability_score'] = min(100, max(0, 100 - (avg_word_length - 5) * 10))
        
        # Generate suggestions for improvement
        if metrics['coverage_score'] < 80:
            metrics['suggestions'].append({
                'type': 'coverage',
                'message': f"Documentation coverage is {metrics['coverage_score']:.1f}%. Consider adding documentation for all public APIs.",
                'severity': 'medium'
            })
            
        if metrics['readability_score'] < 70:
            metrics['suggestions'].append({
                'type': 'readability',
                'message': 'Documentation could be more concise and easier to read.',
                'severity': 'low'
            })
        
        # Calculate overall completeness score (weighted average)
        metrics['completeness_score'] = (
            metrics['coverage_score'] * self.metrics_config['coverage_weight'] +
            metrics['readability_score'] * self.metrics_config['readability_weight'] +
            (100 - (len(metrics['issues']) * 5)) * self.metrics_config['consistency_weight']
        )
        
        return metrics

    def _calculate_overall_score(self, quality_metrics: Dict) -> float:
        """Calculate overall documentation score."""
        return quality_metrics['completeness_score']

    def _score_to_grade(self, score: float) -> str:
        """Convert score to grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """Generate a unified diff between old and new content."""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile='old',
            tofile='new',
            lineterm=''
        )
        return '\n'.join(diff)
    
    def _generate_version_hash(self, content: str) -> str:
        """Generate a hash for version tracking."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def _generate_fallback_documentation(self, content: str, file_extension: str, 
                                       code_structure: Dict) -> str:
        """Generate basic documentation when AI is not available."""
        if file_extension == '.py':
            return self._generate_python_fallback_doc(content, code_structure)
        return f"""# Documentation for {file_extension} file

This is a fallback documentation generated because the OpenAI API key is not configured.

To enable AI-generated documentation, please set the OPENAI_API_KEY environment variable.
"""

    def _generate_python_fallback_doc(self, content: str, code_structure: Dict) -> str:
        """Generate basic Python documentation by analyzing the code structure."""
        doc_parts = ["# Python Module Documentation\n"]
        
        # Add module-level docstring if present
        if code_structure.get('docstring'):
            doc_parts.append(f"\n{code_structure['docstring']}\n")
            
        # Add functions
        if code_structure.get('functions'):
            doc_parts.append("## Functions\n")
            for func in code_structure['functions']:
                doc_parts.append(f"### {func['name']}\n")
                if func.get('docstring'):
                    doc_parts.append(f"{func['docstring']}\n")
                doc_parts.append(f"- **Parameters:** {', '.join(func.get('args', []))}\n")
                if 'returns' in func:
                    doc_parts.append(f"- **Returns:** {func['returns']}\n")
                doc_parts.append("\n")
                
        # Add classes
        if code_structure.get('classes'):
            doc_parts.append("## Classes\n")
            for cls in code_structure['classes']:
                doc_parts.append(f"### {cls['name']}\n")
                if cls.get('docstring'):
                    doc_parts.append(f"{cls['docstring']}\n")
                    
                # Add methods
                if cls.get('methods'):
                    doc_parts.append("#### Methods\n")
                    for method in cls['methods']:
                        doc_parts.append(f"- **{method['name']}**\n")
                        if method.get('docstring'):
                            doc_parts.append(f"  {method['docstring']}\n")
        
        return "".join(doc_parts)

    def _extract_metadata(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Extract metadata from the document content."""
        metadata = {
            'file_type': self.supported_formats.get(file_extension, 'unknown'),
            'size_bytes': len(content.encode('utf-8')),
            'line_count': len(content.splitlines()),
            'has_documentation': self._has_documentation(content, file_extension),
            'last_analyzed': datetime.utcnow().isoformat(),
            'language': self.supported_formats.get(file_extension, 'unknown')
        }
        return metadata

    def _has_documentation(self, content: str, file_extension: str) -> bool:
        """Check if the file has documentation."""
        if file_extension == '.py':
            # Check for module/class/function docstrings
            return '"""' in content or "'''" in content
        elif file_extension in ['.js', '.ts']:
            # Check for JSDoc comments
            return '/**' in content
        elif file_extension == '.md':
            # Markdown files are documentation
            return True
        return False

    def _calculate_docstring_coverage(self, elements: List[Dict]) -> float:
        """Calculate docstring coverage."""
        if not elements:
            return 0.0
        return sum(1 for e in elements if e.get('has_docstring', False)) / len(elements)
        
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """
        Analyze Python code structure using AST.
        
        Args:
            content: The source code to analyze
            
        Returns:
            Dict containing code structure information
        """
        class Analyzer(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.classes = []
                self.imports = []
                self.docstrings = []
                self.ast_errors = []
            
            def visit_FunctionDef(self, node):
                docstring = ast.get_docstring(node)
                if docstring:
                    self.docstrings.append(docstring)
                
                self.functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if hasattr(node, 'returns') and node.returns else None,
                    'line': node.lineno,
                    'end_line': node.end_lineno,
                    'docstring': docstring,
                    'has_docstring': bool(docstring)
                })
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                docstring = ast.get_docstring(node)
                if docstring:
                    self.docstrings.append(docstring)
                
                self.classes.append({
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'line': node.lineno,
                    'end_line': node.end_lineno,
                    'docstring': docstring,
                    'has_docstring': bool(docstring)
                })
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            
            def visit_ImportFrom(self, node):
                for alias in node.names:
                    self.imports.append({
                        'module': node.module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'level': node.level,
                        'line': node.lineno
                    })
        
        try:
            tree = ast.parse(content)
            analyzer = Analyzer()
            analyzer.visit(tree)
            
            return {
                'language': 'python',
                'functions': analyzer.functions,
                'classes': analyzer.classes,
                'imports': analyzer.imports,
                'docstrings': analyzer.docstrings,
                'ast_errors': analyzer.ast_errors,
                'metrics': {
                    'function_count': len(analyzer.functions),
                    'class_count': len(analyzer.classes),
                    'import_count': len(analyzer.imports),
                    'docstring_coverage': self._calculate_docstring_coverage(
                        analyzer.functions + analyzer.classes
                    ) if (analyzer.functions or analyzer.classes) else 0.0
                }
            }
        except SyntaxError as e:
            return {
                'language': 'python',
                'error': f'Syntax error: {str(e)}',
                'line': e.lineno,
                'offset': e.offset
            }

    def _analyze_javascript_code(self, content: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript code structure.
        
        Args:
            content: The source code to analyze
            
        Returns:
            Dict containing code structure information
        """
        # Count functions using regex (basic implementation)
        function_pattern = r'(?:function\s+([a-zA-Z_$][0-9a-zA-Z_$]*)\s*\()|(?:const\s+([a-zA-Z_$][0-9a-zA-Z_$]*)\s*=\s*(?:\([^)]*\)|\w+)\s*=>)'
        functions = []
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                functions.append({
                    'name': func_name,
                    'line': content[:match.start()].count('\n') + 1,
                    'has_docstring': bool(re.search(r'/\*\*[\s\S]*?\*/', content[:match.start()])),
                    'type': 'function' if match.group(1) else 'arrow_function'
                })
        
        # Find class definitions
        class_pattern = r'class\s+([a-zA-Z_$][0-9a-zA-Z_$]*)'
        classes = []
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'has_docstring': bool(re.search(r'/\*\*[\s\S]*?\*/', content[:match.start()]))
            })
        
        # Count JSDoc comments
        jsdoc_comments = re.findall(r'/\*\*[\s\S]*?\*/', content)
        
        # Count imports (ES6)
        imports = []
        import_pattern = r'import\s+(?:{[^}]*}\s+from\s+)?["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, content):
            imports.append({
                'module': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return {
            'language': 'javascript',
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'docstrings': jsdoc_comments,
            'metrics': {
                'function_count': len(functions),
                'class_count': len(classes),
                'import_count': len(imports),
                'docstring_coverage': self._calculate_docstring_coverage(functions + classes)
            }
        }
        
    def _analyze_typescript_code(self, content: str) -> Dict[str, Any]:
        """
        Analyze TypeScript code structure.
        For now, we'll use the same implementation as JavaScript.
        In a real implementation, we would use a TypeScript parser.
        """
        result = self._analyze_javascript_code(content)
        result['language'] = 'typescript'
        return result

    def _analyze_code_structure(self, content: str, file_extension: str) -> Dict:
        """
        Analyze code structure based on file type.
        
        Args:
            content: Source code content
            file_extension: File extension to determine the analyzer
            
        Returns:
            Dict containing analyzed code structure
        """
        analyzer = self.analyzers.get(file_extension)
        if analyzer:
            try:
                return analyzer(content)
            except Exception as e:
                logger.warning(f"Error analyzing {file_extension} code: {str(e)}")
                return {
                    "file_type": self.supported_formats[file_extension],
                    "error": str(e)
                }
        return {
            "file_type": self.supported_formats[file_extension],
            "warning": "No specific analyzer available for this file type"
        }
