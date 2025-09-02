import os
from typing import Dict, List, Optional, Tuple
import openai
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
import numpy as np
from datetime import datetime
import logging

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class AIService:
    """Service for AI-powered document generation and analysis."""
    
    def __init__(self):
        # Initialize sentence transformer model for semantic similarity
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_model = "gpt-4"  # Default model
    
    async def generate_document(
        self,
        document_type: str,
        code_snippets: List[str],
        project_description: str = "",
        existing_docs: List[str] = None,
        **kwargs
    ) -> Dict[str, any]:
        """
        Generate a document (SRS/SDS) based on code snippets and project description.
        
        Args:
            document_type: Type of document to generate ('srs' or 'sds')
            code_snippets: List of code snippets to analyze
            project_description: Description of the project
            existing_docs: List of existing documentation for context
            
        Returns:
            Dictionary containing generated document and suggestions
        """
        try:
            # Prepare the prompt based on document type
            if document_type.lower() == 'srs':
                prompt = self._create_srs_prompt(project_description, code_snippets, existing_docs)
            elif document_type.lower() == 'sds':
                prompt = self._create_sds_prompt(project_description, code_snippets, existing_docs)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional technical writer and software engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the generated content
            generated_content = response.choices[0].message.content
            
            # Analyze the generated content for quality and completeness
            analysis = self.analyze_document_quality(generated_content, document_type)
            
            return {
                "status": "success",
                "document": generated_content,
                "analysis": analysis,
                "suggestions": self._generate_suggestions(analysis, document_type)
            }
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate document: {str(e)}"
            )
    
    def analyze_code_documentation_consistency(
        self, 
        code: str, 
        documentation: str
    ) -> Dict[str, any]:
        """
        Analyze the consistency between code and its documentation.
        
        Args:
            code: Source code
            documentation: Documentation text
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Extract code elements (simplified example)
            code_elements = self._extract_code_elements(code)
            
            # Calculate semantic similarity between code elements and documentation
            similarities = []
            for element in code_elements:
                similarity = self._calculate_semantic_similarity(element, documentation)
                similarities.append({
                    'element': element,
                    'similarity_score': similarity
                })
            
            # Calculate overall consistency score
            avg_similarity = np.mean([s['similarity_score'] for s in similarities])
            
            # Identify potential issues
            issues = []
            for item in similarities:
                if item['similarity_score'] < 0.3:  # Threshold for low similarity
                    issues.append({
                        'element': item['element'],
                        'issue': 'Low documentation coverage',
                        'suggestion': f'Add documentation for: {item["element"][:50]}...'
                    })
            
            return {
                'consistency_score': float(avg_similarity),
                'elements_analyzed': len(similarities),
                'issues_found': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code documentation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze code documentation: {str(e)}"
            )
    
    def analyze_document_quality(
        self, 
        document: str, 
        doc_type: str
    ) -> Dict[str, any]:
        """
        Analyze the quality of a generated document.
        
        Args:
            document: The document text to analyze
            doc_type: Type of document ('srs' or 'sds')
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            # Basic metrics
            word_count = len(document.split())
            section_count = document.count('##')  # Count markdown headers
            
            # Check for required sections based on document type
            required_sections = self._get_required_sections(doc_type)
            missing_sections = []
            
            for section in required_sections:
                if f"## {section}" not in document.lower():
                    missing_sections.append(section)
            
            # Calculate coverage score (0-100%)
            coverage = ((len(required_sections) - len(missing_sections)) / len(required_sections)) * 100
            
            return {
                'word_count': word_count,
                'section_count': section_count,
                'required_sections': required_sections,
                'missing_sections': missing_sections,
                'coverage_score': coverage,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document quality: {str(e)}")
            return {
                'error': str(e),
                'word_count': 0,
                'section_count': 0,
                'coverage_score': 0
            }
    
    def _create_srs_prompt(
        self, 
        project_description: str, 
        code_snippets: List[str],
        existing_docs: List[str] = None
    ) -> str:
        """Create a prompt for generating a Software Requirements Specification."""
        prompt = """
        Create a detailed Software Requirements Specification (SRS) document based on the following:
        
        Project Description:
        {project_description}
        
        Code Snippets:
        {code_snippets}
        
        {existing_docs_section}
        
        The SRS should include the following sections:
        1. Introduction
           - Purpose
           - Document Conventions
           - Intended Audience and Reading Suggestions
           - Product Scope
           - References
        
        2. Overall Description
           - Product Perspective
           - Product Features
           - User Classes and Characteristics
           - Operating Environment
           - Design and Implementation Constraints
           - User Documentation
           - Assumptions and Dependencies
        
        3. System Features and Requirements
           - Functional Requirements
           - External Interface Requirements
           - System Features
           - Non-Functional Requirements
        
        4. Appendices
           - Glossary
           - Analysis Models
           - Issues List
        
        Format the output in markdown with appropriate headers and subheaders.
        """
        
        existing_docs_section = ""
        if existing_docs:
            existing_docs_section = "Existing Documentation:\n" + "\n---\n".join(existing_docs)
        
        return prompt.format(
            project_description=project_description,
            code_snippets="\n\n".join(code_snippets),
            existing_docs_section=existing_docs_section
        )
    
    def _create_sds_prompt(
        self, 
        project_description: str, 
        code_snippets: List[str],
        existing_docs: List[str] = None
    ) -> str:
        """Create a prompt for generating a Software Design Specification."""
        prompt = """
        Create a detailed Software Design Specification (SDS) document based on the following:
        
        Project Description:
        {project_description}
        
        Code Snippets:
        {code_snippets}
        
        {existing_docs_section}
        
        The SDS should include the following sections:
        1. Introduction
           - Purpose
           - Scope
           - Definitions, Acronyms, and Abbreviations
           - References
           
        2. System Overview
           - System Architecture
           - Design Constraints
           
        3. System Design Considerations
           - Assumptions and Dependencies
           - General Constraints
           - Goals and Guidelines
           - Development Methods
           
        4. Architectural Strategies
           - Strategy 1
           - Strategy 2
           
        5. System Architecture
           - Component 1
           - Component 2
           
        6. Detailed System Design
           - Module 1
           - Module 2
           
        7. User Interface Design
           - Overview of User Interface
           - Screen Images
           - Objects and Actions
           
        8. Database Design
           - Database Schema
           - Data Access and Modification
           
        Format the output in markdown with appropriate headers and subheaders.
        """
        
        existing_docs_section = ""
        if existing_docs:
            existing_docs_section = "Existing Documentation:\n" + "\n---\n".join(existing_docs)
        
        return prompt.format(
            project_description=project_description,
            code_snippets="\n\n".join(code_snippets),
            existing_docs_section=existing_docs_section
        )
    
    def _extract_code_elements(self, code: str) -> List[str]:
        """Extract important code elements for documentation analysis."""
        # This is a simplified implementation
        # In a real-world scenario, use a proper code parser for the specific language
        elements = []
        
        # Split code into lines and look for function/class definitions
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def ') or line.startswith('class '):
                elements.append(line)
        
        return elements if elements else ["No identifiable code elements found"]
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # Encode the texts
        embeddings1 = self.similarity_model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.similarity_model.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        return float(cosine_scores[0][0])
    
    def _get_required_sections(self, doc_type: str) -> List[str]:
        """Get the list of required sections for a document type."""
        if doc_type.lower() == 'srs':
            return [
                'introduction',
                'overall description',
                'system features',
                'external interface requirements',
                'non-functional requirements'
            ]
        elif doc_type.lower() == 'sds':
            return [
                'introduction',
                'system overview',
                'system design considerations',
                'architectural strategies',
                'system architecture',
                'detailed system design'
            ]
        return []
    
    def _generate_suggestions(self, analysis: Dict, doc_type: str) -> List[str]:
        """Generate suggestions based on document analysis."""
        suggestions = []
        
        # Check coverage
        if 'coverage_score' in analysis:
            if analysis['coverage_score'] < 50:
                suggestions.append("Document has low coverage. Consider adding more sections.")
            
            if analysis.get('missing_sections'):
                suggestions.append(f"Add missing sections: {', '.join(analysis['missing_sections'])}")
