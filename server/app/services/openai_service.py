import os
from typing import Dict, List, Optional, Literal
import openai
from openai import OpenAI
from pydantic import BaseModel

# Define document types
document_type = Literal["srs", "sds"]

class DocumentGenerationRequest(BaseModel):
    project_description: str
    code_snippets: List[Dict[str, str]]
    document_type: document_type
    additional_context: Optional[str] = None

class OpenAIService:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo"  # or "gpt-4" if you don't have access to turbo

    async def generate_document(self, request: DocumentGenerationRequest) -> str:
        """Generate SRS or SDS document based on project description and code snippets."""
        try:
            # Prepare the system message based on document type
            if request.document_type == "srs":
                system_message = self._get_srs_system_prompt()
            else:  # sds
                system_message = self._get_sds_system_prompt()

            # Prepare the user message with project information
            user_message = self._prepare_user_message(
                request.project_description,
                request.code_snippets,
                request.additional_context
            )

            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error generating document: {str(e)}")

    def _get_srs_system_prompt(self) -> str:
        """Return the system prompt for SRS generation."""
        return """You are a technical writer specializing in creating comprehensive Software Requirements Specification (SRS) documents. 
        Your task is to generate a well-structured SRS document based on the provided project description and code snippets.
        The SRS should follow standard IEEE 830 format and include the following sections:
        1. Introduction
           1.1 Purpose
           1.2 Document Conventions
           1.3 Intended Audience and Reading Suggestions
           1.4 Project Scope
        2. Overall Description
           2.1 Product Perspective
           2.2 Product Features
           2.3 User Classes and Characteristics
           2.4 Operating Environment
           2.5 Design and Implementation Constraints
        3. System Features and Requirements
           3.1 Functional Requirements
           3.2 Non-Functional Requirements
        4. External Interface Requirements
           4.1 User Interfaces
           4.2 Hardware Interfaces
           4.3 Software Interfaces
           4.4 Communication Protocols
        5. Other Non-Functional Requirements
           5.1 Performance Requirements
           5.2 Safety Requirements
           5.3 Security Requirements
        
        Make sure the document is clear, concise, and technically accurate. Use markdown formatting with appropriate headings, lists, and code blocks where necessary."""

    def _get_sds_system_prompt(self) -> str:
        """Return the system prompt for SDS generation."""
        return """You are a software architect specializing in creating detailed Software Design Specification (SDS) documents.
        Your task is to generate a comprehensive SDS document based on the provided project description and code snippets.
        The SDS should follow standard IEEE 1016 format and include the following sections:
        1. Introduction
           1.1 Purpose
           1.2 Scope
           1.3 Definitions, Acronyms, and Abbreviations
        2. System Architecture
           2.1 System Overview
           2.2 Architectural Design
           2.3 Component Diagrams
        3. Detailed Design
           3.1 Module/Component Descriptions
           3.2 Class Diagrams
           3.3 Data Models
           3.4 User Interface Design
        4. Data Design
           4.1 Data Structures
           4.2 Database Schema
        5. Interface Design
           5.1 User Interfaces
           5.2 External APIs
           5.3 Internal Interfaces
        6. Non-Functional Requirements
           6.1 Performance
           6.2 Security
           6.3 Reliability
        7. Implementation Details
           7.1 Development Environment
           7.2 Dependencies
           7.3 Build and Deployment
        
        Use markdown formatting with appropriate headings, code blocks, and diagrams in mermaid format where applicable."""

    def _prepare_user_message(self, 
                            project_description: str, 
                            code_snippets: List[Dict[str, str]],
                            additional_context: str = None) -> str:
        """Prepare the user message with project information."""
        message = f"""# Project Description
{project_description}

# Code Snippets
"""
        # Add code snippets with language and file path if available
        for i, snippet in enumerate(code_snippets, 1):
            message += f"\n## Snippet {i}\n"
            if 'file_path' in snippet and snippet['file_path']:
                message += f"**File:** {snippet['file_path']}\n"
            if 'language' in snippet and snippet['language']:
                message += f"**Language:** {snippet['language']}\n"
            message += f"```{snippet.get('language', '')}\n{snippet['content']}\n```\n"
        
        if additional_context:
            message += f"\n# Additional Context\n{additional_context}\n"
        
        message += """
Please generate a comprehensive document based on the above information.
Ensure the document is well-structured, clear, and technically accurate.
"""
        return message
