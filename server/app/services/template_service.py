import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from ..models.template import Template, TemplateSection, TemplateType, TemplateVariable

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self):
        self.templates: Dict[UUID, Template] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize default SRS and SDS templates."""
        # Default SRS Template
        srs_template = Template(
            name="Standard SRS",
            description="Default Software Requirements Specification template",
            type=TemplateType.SRS,
            is_default=True,
            variables={
                "project_name": "My Project",
                "version": "1.0.0",
                "author": "",
            },
        )
        
        srs_sections = [
            TemplateSection(
                id="introduction",
                title="1. Introduction",
                order=1,
                description="Overview of the document and project",
                content="""## 1.1 Purpose
This document describes the software requirements for {project_name}.

## 1.2 Scope
This project involves the development of [briefly describe the system's purpose].""",
            ),
            # Add more sections as needed
        ]
        
        for section in srs_sections:
            srs_template.add_section(section)
        
        self.create_template(srs_template)

        # Default SDS Template
        sds_template = Template(
            name="Standard SDS",
            description="Default Software Design Specification template",
            type=TemplateType.SDS,
            is_default=True,
            variables={
                "project_name": "My Project",
                "version": "1.0.0",
                "author": "",
            },
        )
        
        sds_sections = [
            TemplateSection(
                id="architecture",
                title="1. System Architecture",
                order=1,
                description="High-level system architecture",
                content="""## 1.1 System Overview
[Provide a high-level overview of the system architecture]

## 1.2 Component Diagram
[Include or describe the component diagram]""",
            ),
            # Add more sections as needed
        ]
        
        for section in sds_sections:
            sds_template.add_section(section)
        
        self.create_template(sds_template)

    def create_template(self, template: Template) -> Template:
        """Create a new template."""
        if template.id in self.templates:
            raise ValueError(f"Template with ID {template.id} already exists")
        
        self.templates[template.id] = template
        logger.info(f"Created template: {template.name} ({template.id})")
        return template

    def get_template(self, template_id: Union[UUID, str]) -> Optional[Template]:
        """Get a template by ID."""
        template_id = UUID(str(template_id))
        return self.templates.get(template_id)

    def get_templates(
        self, 
        template_type: Optional[TemplateType] = None,
        include_default: bool = True
    ) -> List[Template]:
        """Get all templates, optionally filtered by type."""
        templates = list(self.templates.values())
        
        if template_type is not None:
            templates = [t for t in templates if t.type == template_type]
        
        if not include_default:
            templates = [t for t in templates if not t.is_default]
        
        return sorted(templates, key=lambda x: (x.type, x.name))

    def update_template(self, template_id: Union[UUID, str], updates: dict) -> Optional[Template]:
        """Update an existing template."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Create a new template with updated fields
        updated_template = template.copy(update=updates, deep=True)
        updated_template.updated_at = datetime.utcnow()
        
        self.templates[updated_template.id] = updated_template
        logger.info(f"Updated template: {updated_template.name} ({updated_template.id})")
        return updated_template

    def delete_template(self, template_id: Union[UUID, str]) -> bool:
        """Delete a template by ID."""
        template_id = UUID(str(template_id))
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        if template.is_default:
            raise ValueError("Cannot delete default templates")
        
        del self.templates[template_id]
        logger.info(f"Deleted template: {template.name} ({template_id})")
        return True

    def get_default_template(self, template_type: TemplateType) -> Optional[Template]:
        """Get the default template for a given type."""
        for template in self.templates.values():
            if template.type == template_type and template.is_default:
                return template
        return None

    def create_template_from_existing(
        self, 
        source_template_id: Union[UUID, str],
        name: str,
        description: str,
        created_by: Optional[UUID] = None
    ) -> Template:
        """Create a new template based on an existing one."""
        source = self.get_template(source_template_id)
        if not source:
            raise ValueError(f"Source template not found: {source_template_id}")
        
        # Create a deep copy of the source template
        new_template = source.copy(deep=True)
        new_template.id = UUID(int=0)  # Will be regenerated when added
        new_template.name = name
        new_template.description = description
        new_template.is_default = False
        new_template.created_by = created_by
        new_template.created_at = datetime.utcnow()
        new_template.updated_at = datetime.utcnow()
        
        return self.create_template(new_template)

    def render_template(
        self, 
        template_id: Union[UUID, str], 
        context: Optional[Dict] = None,
        include_section_ids: bool = False
    ) -> str:
        """Render a template with the provided context."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        context = context or {}
        rendered_sections = []
        
        for section in sorted(template.sections, key=lambda x: x.order):
            try:
                section_content = section.content.format(**template.variables, **context)
                if include_section_ids:
                    rendered_sections.append(f"<!-- section:{section.id} -->\n# {section.title}\n\n{section_content}")
                else:
                    rendered_sections.append(f"# {section.title}\n\n{section_content}")
            except KeyError as e:
                logger.warning(f"Missing variable {e} in template section {section.id}")
                continue
                
        return "\n\n".join(rendered_sections)
