from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# In-memory storage (replace with database in production)
project_inputs_db = {}

class CodeSnippet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    language: str
    content: str
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    author: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    line_number: Optional[int] = None
    file_path: Optional[str] = None

class UserPrompt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    context: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = {}

class ProjectInput(BaseModel):
    project_id: str
    code_snippets: List[CodeSnippet] = []
    comments: List[Comment] = []
    user_prompts: List[UserPrompt] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

@router.post("/projects/{project_id}/inputs")
async def create_project_input(project_id: str, project_input: ProjectInput):
    if project_id in project_inputs_db:
        raise HTTPException(status_code=400, detail="Project input already exists")
    
    project_inputs_db[project_id] = project_input
    return {"message": "Project input created successfully", "project_id": project_id}

@router.get("/projects/{project_id}/inputs")
async def get_project_inputs(project_id: str):
    if project_id not in project_inputs_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_inputs_db[project_id]

@router.post("/projects/{project_id}/code")
async def add_code_snippet(project_id: str, code_snippet: CodeSnippet):
    if project_id not in project_inputs_db:
        project_inputs_db[project_id] = ProjectInput(project_id=project_id)
    
    project_inputs_db[project_id].code_snippets.append(code_snippet)
    project_inputs_db[project_id].updated_at = datetime.utcnow()
    return {"message": "Code snippet added successfully", "snippet_id": code_snippet.id}

@router.post("/projects/{project_id}/comments")
async def add_comment(project_id: str, comment: Comment):
    if project_id not in project_inputs_db:
        project_inputs_db[project_id] = ProjectInput(project_id=project_id)
    
    project_inputs_db[project_id].comments.append(comment)
    project_inputs_db[project_id].updated_at = datetime.utcnow()
    return {"message": "Comment added successfully", "comment_id": comment.id}

@router.post("/projects/{project_id}/prompts")
async def add_user_prompt(project_id: str, prompt: UserPrompt):
    if project_id not in project_inputs_db:
        project_inputs_db[project_id] = ProjectInput(project_id=project_id)
    
    project_inputs_db[project_id].user_prompts.append(prompt)
    project_inputs_db[project_id].updated_at = datetime.utcnow()
    return {"message": "User prompt added successfully", "prompt_id": prompt.id}

@router.get("/projects/{project_id}/search")
async def search_inputs(project_id: str, query: str):
    if project_id not in project_inputs_db:
        return {"code_snippets": [], "comments": [], "user_prompts": []}
    
    project = project_inputs_db[project_id]
    
    # Simple search implementation (replace with proper search in production)
    results = {
        "code_snippets": [
            snippet for snippet in project.code_snippets 
            if query.lower() in snippet.content.lower() or 
               (snippet.file_path and query.lower() in snippet.file_path.lower())
        ],
        "comments": [
            comment for comment in project.comments 
            if query.lower() in comment.content.lower()
        ],
        "user_prompts": [
            prompt for prompt in project.user_prompts 
            if query.lower() in prompt.content.lower()
        ]
    }
    
    return results
