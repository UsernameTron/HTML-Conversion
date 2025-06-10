"""Data models for styling configuration using Pydantic for validation."""

from typing import Dict, Any, Optional, Annotated, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
import json


class StyleConfig(BaseModel):
    """Configuration model for styling options with validation."""
    
    # Typography
    font_family: str = Field(default="Inter, -apple-system, BlinkMacSystemFont, sans-serif")
    font_size: int = Field(default=18, ge=12, le=72)
    font_weight: str = Field(default="400", pattern=r"^(300|400|500|600|700)$")
    line_height: float = Field(default=1.6, ge=1.0, le=3.0)
    letter_spacing: int = Field(default=0, ge=-2, le=5)
    
    # Colors
    text_color: str = Field(default="#333333", pattern=r"^#[0-9a-fA-F]{6}$")  # Changed default to #333333
    background_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    accent_color: str = Field(default="#4285f4", pattern=r"^#[0-9a-fA-F]{6}$")
    
    # Layout
    text_align: str = Field(default="left", pattern=r"^(left|center|right|justify)$")
    margin: int = Field(default=24, ge=0, le=100)
    padding: int = Field(default=32, ge=0, le=100)
    border_radius: int = Field(default=8, ge=0, le=50)
    max_width: int = Field(default=900, ge=600, le=1400)
    
    # Advanced options
    add_shadows: bool = Field(default=True)
    add_gradients: bool = Field(default=False)
    modern_typography: bool = Field(default=True)
    responsive_design: bool = Field(default=True)
    
    model_config = {
        "validate_assignment": True,
        "use_enum_values": True
    }
    
    def to_json(self) -> str:
        """Export configuration as JSON string."""
        return json.dumps(self.dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StyleConfig':
        """Create configuration from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    @field_validator('text_color', mode='before')
    def normalize_text_color(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class FileUploadModel(BaseModel):
    """Model for file upload validation."""
    
    filename: str
    file_size: int = Field(ge=0, le=50_000_000)  # Max 50MB
    file_type: str
    content: Optional[bytes] = None
    
    @field_validator('filename')
    def validate_filename(cls, v):
        """Validate filename for security."""
        if not v or len(v) > 255:
            raise ValueError("Invalid filename length")
        
        # Check for path traversal
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Invalid filename characters")
        
        return v
    
    @field_validator('file_type')
    def validate_file_type(cls, v):
        """Validate allowed file types."""
        allowed_types = {
            'text/plain', 'text/markdown', 'text/csv', 'application/json',
            'text/html', 'text/css', 'text/javascript',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/png', 'image/jpeg', 'image/gif', 'image/bmp'
        }
        
        if v not in allowed_types:
            raise ValueError(f"File type {v} not allowed")
        
        return v


class SecurityConfig(BaseModel):
    """Security configuration model."""
    # Add compatibility for max_file_size_mb and blocked_patterns
    max_file_size: int = Field(default=50_000_000)  # 50MB
    max_file_size_mb: int = Field(default=10)  # For test compatibility
    max_text_length: int = Field(default=1_000_000)  # 1MB text
    allowed_html_tags: list = Field(default_factory=lambda: [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'div', 'span', 'code', 'pre'
    ])
    allowed_html_attributes: dict = Field(default_factory=lambda: {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'div': ['class', 'id'],
        'span': ['class', 'id'],
        'p': ['class', 'id'],
        '*': ['style']
    })
    allowed_file_types: list = Field(default_factory=lambda: ['txt', 'md', 'pdf', 'docx', 'html', 'css', 'json', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])
    blocked_patterns: list = Field(default_factory=lambda: ['<script', 'javascript:', 'onclick=', 'onerror='])

    def __init__(self, **data):
        # Allow max_file_size_mb to override max_file_size for test compatibility
        if 'max_file_size_mb' in data:
            data['max_file_size'] = int(data['max_file_size_mb']) * 1_000_000
        super().__init__(**data)
    
    model_config = {
        "validate_assignment": True
    }