"""
Unit tests for data models and validation.
"""

import pytest
from pydantic import ValidationError
from models.style_models import StyleConfig, SecurityConfig
from models.template_models import Template, TemplateMetadata, ContentPlaceholder, TemplateCategory


class TestStyleModels:
    """Test style configuration models."""
    
    def test_style_config_defaults(self):
        """Test StyleConfig with default values."""
        config = StyleConfig()
        assert config.font_size == 18
        assert config.text_color == "#333333"
        assert config.background_color == "#ffffff"
        assert config.font_family == "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    
    def test_style_config_validation(self):
        """Test StyleConfig validation."""
        # Valid configuration
        config = StyleConfig(
            font_size=16,
            text_color="#FF0000",
            background_color="#FFFFFF",
            font_family="Arial, sans-serif"
        )
        assert config.font_size == 16
        assert config.text_color == "#ff0000"  # Should be lowercase
    
    def test_style_config_invalid_font_size(self):
        """Test StyleConfig with invalid font size."""
        with pytest.raises(ValidationError):
            StyleConfig(font_size=5)  # Too small
        
        with pytest.raises(ValidationError):
            StyleConfig(font_size=100)  # Too large
    
    def test_style_config_invalid_color(self):
        """Test StyleConfig with invalid color format."""
        with pytest.raises(ValidationError):
            StyleConfig(text_color="invalid-color")
        
        with pytest.raises(ValidationError):
            StyleConfig(background_color="#GGGGGG")  # Invalid hex
    
    def test_security_config(self):
        """Test SecurityConfig initialization."""
        config = SecurityConfig()
        assert config.max_file_size_mb == 10
        assert config.max_text_length == 1000000
        assert len(config.allowed_file_types) > 0
        assert 'txt' in config.allowed_file_types


class TestTemplateModels:
    """Test template system models."""
    
    def test_content_placeholder_basic(self):
        """Test basic ContentPlaceholder creation."""
        placeholder = ContentPlaceholder(
            key="test_key",
            label="Test Label",
            description="Test description",
            placeholder_text="Test placeholder"
        )
        assert placeholder.key == "test_key"
        assert placeholder.label == "Test Label"
        assert placeholder.required is True  # Default
        assert placeholder.content_type == "text"  # Default
    
    def test_content_placeholder_key_validation(self):
        """Test ContentPlaceholder key validation."""
        # Valid keys
        valid_keys = ["test_key", "test-key", "testkey123", "test_key_123"]
        for key in valid_keys:
            placeholder = ContentPlaceholder(
                key=key,
                label="Test",
                description="Test",
                placeholder_text="Test"
            )
            assert placeholder.key == key.lower()
        
        # Invalid keys
        with pytest.raises(ValidationError):
            ContentPlaceholder(
                key="test key",  # Space not allowed
                label="Test",
                description="Test",
                placeholder_text="Test"
            )
    
    def test_template_metadata(self):
        """Test TemplateMetadata creation."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            category=TemplateCategory.BUSINESS,
            tags=["test", "business"]
        )
        assert metadata.name == "Test Template"
        assert metadata.category == TemplateCategory.BUSINESS
        assert "test" in metadata.tags
        assert metadata.author == "HTML Formatter Pro"  # Default
    
    def test_template_creation(self):
        """Test Template creation and validation."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            category=TemplateCategory.BUSINESS
        )
        
        placeholder = ContentPlaceholder(
            key="title",
            label="Title",
            description="Document title",
            placeholder_text="Enter title"
        )
        
        template = Template(
            id="test_template",
            metadata=metadata,
            html_template="<h1>{{title}}</h1>",
            placeholders=[placeholder]
        )
        
        assert template.id == "test_template"
        assert len(template.placeholders) == 1
        assert template.metadata.name == "Test Template"
    
    def test_template_rendering(self):
        """Test template rendering with content."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            category=TemplateCategory.BUSINESS
        )
        
        placeholder = ContentPlaceholder(
            key="title",
            label="Title",
            description="Document title",
            placeholder_text="Default Title"
        )
        
        template = Template(
            id="test_template",
            metadata=metadata,
            html_template="<h1>{{title}}</h1><p>Content here</p>",
            placeholders=[placeholder]
        )
        
        # Test rendering with content
        content_data = {"title": "My Custom Title"}
        rendered = template.render(content_data)
        assert "My Custom Title" in rendered
        assert "<h1>My Custom Title</h1>" in rendered
        
        # Test rendering without content (should use placeholder)
        rendered_default = template.render({})
        assert "Default Title" in rendered_default
    
    def test_template_validation(self):
        """Test template content validation."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            category=TemplateCategory.BUSINESS
        )
        
        # Required placeholder
        required_placeholder = ContentPlaceholder(
            key="required_field",
            label="Required Field",
            description="This field is required",
            placeholder_text="Enter value",
            required=True
        )
        
        # Optional placeholder with length limit
        optional_placeholder = ContentPlaceholder(
            key="optional_field",
            label="Optional Field",
            description="This field is optional",
            placeholder_text="Enter value",
            required=False,
            max_length=50
        )
        
        template = Template(
            id="test_template",
            metadata=metadata,
            html_template="<h1>{{required_field}}</h1><p>{{optional_field}}</p>",
            placeholders=[required_placeholder, optional_placeholder]
        )
        
        # Test missing required field
        errors = template.validate_content({"optional_field": "Some value"})
        assert len(errors) > 0
        assert "required" in errors[0].lower()
        
        # Test content too long
        errors = template.validate_content({
            "required_field": "Valid value",
            "optional_field": "A" * 100  # Exceeds max_length of 50
        })
        assert len(errors) > 0
        assert "maximum length" in errors[0].lower()
        
        # Test valid content
        errors = template.validate_content({
            "required_field": "Valid value",
            "optional_field": "Short value"
        })
        assert len(errors) == 0
    
    def test_template_id_validation(self):
        """Test template ID validation."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            category=TemplateCategory.BUSINESS
        )
        
        # Valid IDs
        valid_ids = ["test_template", "test-template", "template123"]
        for template_id in valid_ids:
            template = Template(
                id=template_id,
                metadata=metadata,
                html_template="<h1>Test</h1>",
                placeholders=[]
            )
            assert template.id == template_id.lower()
        
        # Invalid ID
        with pytest.raises(ValidationError):
            Template(
                id="invalid template id",  # Space not allowed
                metadata=metadata,
                html_template="<h1>Test</h1>",
                placeholders=[]
            )