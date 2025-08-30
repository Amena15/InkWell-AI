from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from ..models.template import (
    Template,
    TemplateSection,
    TemplateType,
    TemplateVariable,
    TemplateCreate,
    TemplateUpdate,
)
from ..services.template_service import TemplateService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize template service
template_service = TemplateService()

@router.get("/", response_model=List[Template])
async def list_templates(
    template_type: Optional[TemplateType] = None,
    include_default: bool = True
):
    """List all available templates, optionally filtered by type."""
    try:
        return template_service.get_templates(
            template_type=template_type,
            include_default=include_default
        )
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates"
        )

@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a specific template by ID."""
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found: {template_id}"
            )
        return template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template"
        )

@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(template_data: TemplateCreate):
    """Create a new template."""
    try:
        # Convert Pydantic model to dict and remove None values
        template_dict = template_data.dict(exclude_unset=True)
        template = Template(**template_dict)
        return template_service.create_template(template)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )

@router.put("/{template_id}", response_model=Template)
async def update_template(template_id: str, template_data: TemplateUpdate):
    """Update an existing template."""
    try:
        # Get existing template
        existing = template_service.get_template(template_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found: {template_id}"
            )
        
        # Update fields from the request
        update_data = template_data.dict(exclude_unset=True)
        updated_template = template_service.update_template(template_id, update_data)
        
        if not updated_template:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update template"
            )
            
        return updated_template
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str):
    """Delete a template by ID."""
    try:
        if not template_service.delete_template(template_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found: {template_id}"
            )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )

@router.post("/{template_id}/duplicate", response_model=Template)
async def duplicate_template(
    template_id: str,
    name: str,
    description: Optional[str] = None,
    created_by: Optional[str] = None
):
    """Create a copy of an existing template."""
    try:
        new_template = template_service.create_template_from_existing(
            source_template_id=template_id,
            name=name,
            description=description or f"Copy of {template_id}",
            created_by=UUID(created_by) if created_by else None
        )
        return new_template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error duplicating template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate template"
        )

@router.post("/{template_id}/render", response_model=Dict[str, Any])
async def render_template(
    template_id: str,
    context: Optional[Dict[str, Any]] = None,
    include_section_ids: bool = False
):
    """Render a template with the provided context."""
    try:
        content = template_service.render_template(
            template_id=template_id,
            context=context or {},
            include_section_ids=include_section_ids
        )
        
        # Get the template to include metadata in the response
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template not found: {template_id}"
            )
            
        return {
            "template_id": str(template.id),
            "template_name": template.name,
            "template_type": template.type,
            "content": content,
            "variables": template.variables,
            "sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "description": section.description,
                    "order": section.order,
                    "required": section.required,
                    "variables": [v.dict() for v in section.variables]
                }
                for section in template.sections
            ]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rendering template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to render template"
        )

# Register the router in your FastAPI app:
# from fastapi import FastAPI
# from .api.templates import router as templates_router
# app = FastAPI()
# app.include_router(templates_router, prefix="/api/templates", tags=["templates"])
