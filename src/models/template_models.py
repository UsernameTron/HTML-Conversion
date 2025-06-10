"""Template system data models and validation."""

from typing import Dict, List, Any, Optional, Union, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import json
from datetime import datetime


# Import HTMLSanitizer for security
def _get_html_sanitizer():
    """Get HTMLSanitizer instance lazily to avoid circular imports."""
    try:
        from utils.sanitizers import HTMLSanitizer
        return HTMLSanitizer()
    except ImportError:
        # Fallback sanitization using simple regex
        import re
        class FallbackSanitizer:
            def sanitize(self, html_content: str) -> str:
                if not html_content:
                    return ""
                # Remove script tags and their content
                clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                # Remove dangerous attributes
                dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
                for attr in dangerous_attrs:
                    clean_html = re.sub(f'{attr}=["\'][^"\']*["\']', '', clean_html, flags=re.IGNORECASE)
                # Remove javascript: URLs
                clean_html = re.sub(r'href=["\']javascript:[^"\']*["\']', '', clean_html, flags=re.IGNORECASE)
                return clean_html
        return FallbackSanitizer()


class TemplateCategory(str, Enum):
    """Template categories for organization."""
    BUSINESS = "business"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    MARKETING = "marketing"


class ContentPlaceholder(BaseModel):
    """Content placeholder configuration."""
    key: str = Field(..., description="Unique placeholder key")
    label: str = Field(..., description="Human-readable label")
    description: str = Field(..., description="Description of expected content")
    placeholder_text: str = Field(..., description="Default placeholder text")
    content_type: str = Field(default="text", description="Type of content expected")
    required: bool = Field(default=True, description="Whether this placeholder is required")
    max_length: Optional[int] = Field(None, description="Maximum content length")
    validation_pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    
    @field_validator('key')
    def validate_key(cls, v):
        """Validate placeholder key format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Placeholder key must be alphanumeric with underscores/hyphens")
        return v.lower()


class StyleOverride(BaseModel):
    """Style override configuration."""
    property: str = Field(..., description="CSS property to override")
    value: str = Field(..., description="CSS value")
    selector: str = Field(default="body", description="CSS selector")
    important: bool = Field(default=False, description="Add !important flag")


class TemplateMetadata(BaseModel):
    """Template metadata and configuration."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: TemplateCategory = Field(..., description="Template category")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    author: str = Field(default="HTML Formatter Pro", description="Template author")
    version: str = Field(default="1.0.0", description="Template version")
    created_date: datetime = Field(default_factory=datetime.now, description="Creation date")
    modified_date: datetime = Field(default_factory=datetime.now, description="Last modification date")
    difficulty_level: str = Field(default="beginner", description="Difficulty level")
    estimated_time: str = Field(default="5 minutes", description="Estimated completion time")
    preview_image: Optional[str] = Field(None, description="Preview image URL")


class Template(BaseModel):
    """Complete template configuration."""
    id: str = Field(..., description="Unique template identifier")
    metadata: TemplateMetadata = Field(..., description="Template metadata")
    html_template: str = Field(..., description="HTML template with placeholders")
    style_overrides: List[StyleOverride] = Field(default_factory=list, description="Style customizations")
    placeholders: List[ContentPlaceholder] = Field(default_factory=list, description="Content placeholders")
    default_style_config: Dict[str, Any] = Field(default_factory=dict, description="Default style configuration")
    sample_content: Dict[str, str] = Field(default_factory=dict, description="Sample content for placeholders")
    
    @field_validator('id')
    def validate_id(cls, v):
        """Validate template ID format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Template ID must be alphanumeric with underscores/hyphens")
        return v.lower()
    
    def render(self, content_data: Dict[str, str], style_config: Optional[Dict[str, Any]] = None) -> str:
        """Render template with provided content."""
        html = self.html_template
        
        # Get sanitizer instance
        sanitizer = _get_html_sanitizer()
        
        # Replace placeholders with sanitized content
        for placeholder in self.placeholders:
            placeholder_value = content_data.get(placeholder.key, placeholder.placeholder_text)
            # Sanitize the placeholder value to prevent XSS
            if placeholder_value:
                sanitized_value = sanitizer.sanitize(str(placeholder_value))
            else:
                sanitized_value = ""
            html = html.replace(f"{{{{{placeholder.key}}}}}", sanitized_value)
        
        # Apply style overrides
        if self.style_overrides:
            style_css = self._generate_override_css()
            html = html.replace("</head>", f"<style>{style_css}</style></head>")
        
        return html
    
    def _generate_override_css(self) -> str:
        """Generate CSS from style overrides."""
        css_rules = []
        for override in self.style_overrides:
            importance = " !important" if override.important else ""
            css_rules.append(f"{override.selector} {{ {override.property}: {override.value}{importance}; }}")
        return "\n".join(css_rules)
    
    def get_required_placeholders(self) -> List[ContentPlaceholder]:
        """Get list of required placeholders."""
        return [p for p in self.placeholders if p.required]
    
    def validate_content(self, content_data: Dict[str, str]) -> List[str]:
        """Validate provided content against template requirements."""
        errors = []
        
        for placeholder in self.placeholders:
            if placeholder.required and placeholder.key not in content_data:
                errors.append(f"Required placeholder '{placeholder.label}' is missing")
            
            if placeholder.key in content_data:
                content = content_data[placeholder.key]
                
                # Length validation
                if placeholder.max_length and len(content) > placeholder.max_length:
                    errors.append(f"'{placeholder.label}' exceeds maximum length of {placeholder.max_length}")
                
                # Pattern validation
                if placeholder.validation_pattern:
                    import re
                    if not re.match(placeholder.validation_pattern, content):
                        errors.append(f"'{placeholder.label}' does not match required format")
        
        return errors
    
    def to_json(self) -> str:
        """Export template as JSON."""
        return json.dumps(self.dict(), indent=2, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        """Create template from JSON."""
        data = json.loads(json_str)
        return cls(**data)


class TemplateLibrary(BaseModel):
    """Collection of templates with management capabilities."""
    templates: Dict[str, Template] = Field(default_factory=dict, description="Template collection")
    categories: Dict[TemplateCategory, List[str]] = Field(default_factory=dict, description="Category organization")
    
    def add_template(self, template: Template) -> bool:
        """Add template to library."""
        if template.id in self.templates:
            return False
        
        self.templates[template.id] = template
        
        # Update category index
        category = template.metadata.category
        if category not in self.categories:
            self.categories[category] = []
        
        if template.id not in self.categories[category]:
            self.categories[category].append(template.id)
        
        return True
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[Template]:
        """Get all templates in a category."""
        template_ids = self.categories.get(category, [])
        return [self.templates[tid] for tid in template_ids if tid in self.templates]
    
    def search_templates(self, query: str) -> List[Template]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            # Search in name and description
            if (query_lower in template.metadata.name.lower() or 
                query_lower in template.metadata.description.lower()):
                results.append(template)
                continue
            
            # Search in tags
            for tag in template.metadata.tags:
                if query_lower in tag.lower():
                    results.append(template)
                    break
        
        return results
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = {
            'total_templates': len(self.templates),
            'categories': {cat.value: len(templates) for cat, templates in self.categories.items()},
            'recent_templates': []
        }
        
        # Get 5 most recent templates
        sorted_templates = sorted(
            self.templates.values(),
            key=lambda t: t.metadata.created_date,
            reverse=True
        )
        stats['recent_templates'] = [t.id for t in sorted_templates[:5]]
        
        return stats