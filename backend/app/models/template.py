from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID, uuid4

class TemplateType(str, Enum):
    SRS = "srs"
    SDS = "sds"
    CUSTOM = "custom"

class TemplateVariable(BaseModel):
    name: str
    description: str
    default_value: Optional[str] = None
    required: bool = True

class TemplateSection(BaseModel):
    id: str
    title: str
    content: str
    description: Optional[str] = None
    variables: List[TemplateVariable] = []
    order: int = 0
    required: bool = True

class TemplateBase(BaseModel):
    name: str
    description: str
    type: TemplateType
    is_default: bool = False
    created_by: Optional[UUID] = None
    version: str = "1.0.0"

class TemplateCreate(TemplateBase):
    sections: List[TemplateSection] = []
    variables: Dict[str, str] = {}

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TemplateType] = None
    is_default: Optional[bool] = None
    version: Optional[str] = None

class Template(TemplateBase):
    id: UUID = Field(default_factory=uuid4)
    sections: List[TemplateSection] = []
    variables: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_section(self, section: TemplateSection) -> None:
        """Add or update a section in the template."""
        existing_index = next(
            (i for i, s in enumerate(self.sections) if s.id == section.id),
            None
        )
        
        if existing_index is not None:
            self.sections[existing_index] = section
        else:
            self.sections.append(section)
        
        self.updated_at = datetime.utcnow()

    def remove_section(self, section_id: str) -> bool:
        """Remove a section from the template by ID."""
        initial_length = len(self.sections)
        self.sections = [s for s in self.sections if s.id != section_id]
        removed = len(self.sections) < initial_length
        if removed:
            self.updated_at = datetime.utcnow()
        return removed

    def render(self, context: Optional[Dict] = None) -> str:
        """Render the template with the provided context."""
        context = context or {}
        rendered_sections = []
        
        for section in sorted(self.sections, key=lambda x: x.order):
            try:
                # First apply template variables
                section_content = section.content.format(**self.variables)
                # Then apply context variables
                section_content = section_content.format(**context)
                rendered_sections.append(f"# {section.title}\n\n{section_content}")
            except KeyError as e:
                # Skip sections with missing variables for now
                continue
                
        return "\n\n".join(rendered_sections)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
