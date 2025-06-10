"""
Integration tests for services and business logic.
"""

import pytest
import tempfile
import os
from services.template_service import TemplateService
from services.html_generator import HTMLGenerator
from services.file_processor import FileProcessor
from models.template_models import TemplateCategory
from models.style_models import StyleConfig, SecurityConfig
from utils.sanitizers import HTMLSanitizer
from utils.validators import FileValidator


class TestTemplateService:
    """Test template service functionality."""
    
    def test_template_service_initialization(self, template_service):
        """Test TemplateService initialization."""
        assert template_service is not None
        assert hasattr(template_service, 'template_library')
        assert len(template_service.template_library.templates) > 0
    
    def test_get_template_library(self, template_service):
        """Test getting the complete template library."""
        library = template_service.get_template_library()
        assert library is not None
        assert len(library.templates) > 0
        assert hasattr(library, 'categories')
    
    def test_get_template_by_id(self, template_service):
        """Test retrieving a specific template by ID."""
        # Get a known template
        template = template_service.get_template('business_letter')
        assert template is not None
        assert template.id == 'business_letter'
        assert template.metadata.name is not None
        assert len(template.placeholders) > 0
    
    def test_get_templates_by_category(self, template_service):
        """Test retrieving templates by category."""
        business_templates = template_service.get_templates_by_category(TemplateCategory.BUSINESS)
        assert len(business_templates) > 0
        
        for template in business_templates:
            assert template.metadata.category == TemplateCategory.BUSINESS
    
    def test_search_templates(self, template_service):
        """Test template search functionality."""
        # Search by name
        results = template_service.search_templates('business')
        assert len(results) > 0
        
        # Search by tag
        results = template_service.search_templates('letter')
        assert len(results) > 0
        
        # Search for non-existent term
        results = template_service.search_templates('nonexistent_term_xyz')
        assert len(results) == 0
    
    def test_render_template(self, template_service):
        """Test template rendering with content."""
        # Get a template
        template = template_service.get_template('business_letter')
        assert template is not None
        
        # Prepare sample content
        content_data = {
            'company_name': 'Test Corp',
            'document_title': 'Test Letter',
            'date': 'December 9, 2024',
            'recipient_name': 'John Doe',
            'subject': 'Test Subject',
            'letter_content': '<p>This is test content.</p>'
        }
        
        # Fill in all required placeholders
        for placeholder in template.get_required_placeholders():
            if placeholder.key not in content_data:
                content_data[placeholder.key] = placeholder.placeholder_text
        
        # Render template
        rendered = template_service.render_template('business_letter', content_data)
        assert rendered is not None
        assert 'Test Corp' in rendered
        assert 'John Doe' in rendered
        assert 'Test Subject' in rendered
    
    def test_render_template_validation_failure(self, template_service):
        """Test template rendering with invalid content."""
        # Try to render without required content
        rendered = template_service.render_template('business_letter', {})
        assert rendered is None  # Should fail validation


class TestHTMLGenerator:
    """Test HTML generation service."""
    
    def test_html_generator_initialization(self, style_config):
        """Test HTMLGenerator initialization."""
        generator = HTMLGenerator(style_config)
        assert generator is not None
        assert generator.style_config == style_config
    
    def test_generate_css(self, style_config):
        """Test CSS generation from style configuration."""
        generator = HTMLGenerator(style_config)
        css = generator.generate_css()
        
        assert isinstance(css, str)
        assert len(css) > 0
        assert f'font-size: {style_config.font_size}px' in css
        assert f'color: {style_config.text_color}' in css
        assert f'background-color: {style_config.background_color}' in css
    
    def test_generate_html_document(self, style_config):
        """Test complete HTML document generation."""
        generator = HTMLGenerator(style_config)
        content = "<h1>Test Title</h1><p>Test content paragraph.</p>"
        
        html_doc = generator.generate_html_document(content)
        
        # Check document structure
        assert '<!DOCTYPE html>' in html_doc
        assert '<html lang="en">' in html_doc
        assert '<head>' in html_doc
        assert '<body>' in html_doc
        assert '</html>' in html_doc
        
        # Check content inclusion
        assert 'Test Title' in html_doc
        assert 'Test content paragraph' in html_doc
        
        # Check security headers
        assert 'Content-Security-Policy' in html_doc
        assert 'Permissions-Policy' in html_doc
    
    def test_security_headers_generation(self, style_config):
        """Test security headers in generated HTML."""
        generator = HTMLGenerator(style_config)
        content = "<p>Test content</p>"
        
        html_doc = generator.generate_html_document(content)
        
        # Check for security headers
        security_headers = [
            'Content-Security-Policy',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        for header in security_headers:
            assert header in html_doc
    
    def test_responsive_design_generation(self, style_config):
        """Test responsive design elements in generated HTML."""
        generator = HTMLGenerator(style_config)
        content = "<p>Test content</p>"
        
        html_doc = generator.generate_html_document(content)
        
        # Check for responsive design elements
        assert 'viewport' in html_doc
        assert 'width=device-width' in html_doc
        assert '@media' in html_doc


class TestFileProcessor:
    """Test file processing service."""
    
    def test_file_processor_initialization(self, html_sanitizer):
        """Test FileProcessor initialization."""
        file_validator = FileValidator()
        processor = FileProcessor(html_sanitizer, file_validator)
        assert processor is not None
    
    def test_process_text_file(self, html_sanitizer, temp_file):
        """Test processing a text file."""
        file_validator = FileValidator()
        processor = FileProcessor(html_sanitizer, file_validator)
        
        # Process the temporary file
        result = processor.process_file(temp_file)
        
        assert result is not None
        assert 'success' in result
        if result['success']:
            assert 'content' in result
            assert len(result['content']) > 0
    
    def test_detect_file_type(self, html_sanitizer):
        """Test file type detection."""
        file_validator = FileValidator()
        processor = FileProcessor(html_sanitizer, file_validator)
        
        # Test different file extensions
        assert processor._detect_file_type('document.txt') == 'text'
        assert processor._detect_file_type('document.pdf') == 'pdf'
        assert processor._detect_file_type('document.docx') == 'docx'
        assert processor._detect_file_type('document.unknown') == 'unknown'
    
    def test_invalid_file_handling(self, html_sanitizer):
        """Test handling of invalid files."""
        file_validator = FileValidator()
        processor = FileProcessor(html_sanitizer, file_validator)
        
        # Test with non-existent file
        result = processor.process_file('/nonexistent/file.txt')
        assert result is not None
        assert not result['success']
        assert 'error' in result


class TestServiceIntegration:
    """Test integration between services."""
    
    def test_template_to_html_generation(self, template_service, style_config):
        """Test integration from template rendering to HTML generation."""
        # Get template
        template = template_service.get_template('business_letter')
        assert template is not None
        
        # Prepare content
        content_data = {}
        for placeholder in template.placeholders:
            content_data[placeholder.key] = placeholder.placeholder_text
        
        # Render template
        rendered_content = template_service.render_template('business_letter', content_data)
        assert rendered_content is not None
        
        # Generate final HTML document
        generator = HTMLGenerator(style_config)
        final_html = generator.generate_html_document(rendered_content)
        
        assert final_html is not None
        assert '<!DOCTYPE html>' in final_html
        assert len(final_html) > len(rendered_content)  # Should be expanded
    
    def test_file_processing_to_html_generation(self, html_sanitizer, style_config, temp_file):
        """Test integration from file processing to HTML generation."""
        file_validator = FileValidator()
        processor = FileProcessor(html_sanitizer, file_validator)
        
        # Process file
        result = processor.process_file(temp_file)
        
        if result['success']:
            # Generate HTML from processed content
            generator = HTMLGenerator(style_config)
            final_html = generator.generate_html_document(result['content'])
            
            assert final_html is not None
            assert '<!DOCTYPE html>' in final_html
            assert 'Test content for file processing' in final_html
    
    def test_security_integration_across_services(self, template_service, html_sanitizer, style_config):
        """Test security integration across all services."""
        # Create malicious template content
        malicious_content = {
            'company_name': 'Safe Corp',
            'document_title': '<script>alert("XSS")</script>Safe Title',
            'letter_content': '<p>Safe content</p><script>maliciousFunction()</script>'
        }
        
        # Get template
        template = template_service.get_template('business_letter')
        if template:
            # Fill required fields
            for placeholder in template.get_required_placeholders():
                if placeholder.key not in malicious_content:
                    malicious_content[placeholder.key] = placeholder.placeholder_text
            
            # Render template (should sanitize content)
            rendered = template_service.render_template('business_letter', malicious_content)
            
            if rendered:
                # Generate final HTML
                generator = HTMLGenerator(style_config)
                final_html = generator.generate_html_document(rendered)
                
                # Verify malicious content is removed (but allow legitimate scripts from HTMLGenerator)
                assert 'alert("XSS")' not in final_html
                assert 'alert(' not in final_html
                assert 'maliciousFunction' not in final_html
                
                # Verify safe content remains
                assert 'Safe Corp' in final_html
                assert 'Safe Title' in final_html
                assert 'Safe content' in final_html


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""
    
    def test_template_loading_performance(self):
        """Test template loading performance."""
        import time
        
        start_time = time.time()
        service = TemplateService()
        end_time = time.time()
        
        loading_time = end_time - start_time
        
        # Should load templates quickly (< 2 seconds)
        assert loading_time < 2.0
        assert len(service.template_library.templates) > 0
    
    def test_html_generation_performance(self, style_config):
        """Test HTML generation performance."""
        import time
        
        generator = HTMLGenerator(style_config)
        large_content = "<p>Content paragraph. " * 1000 + "</p>"
        
        start_time = time.time()
        html_doc = generator.generate_html_document(large_content)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should generate HTML quickly (< 1 second for 1000 paragraphs)
        assert generation_time < 1.0
        assert len(html_doc) > len(large_content)
    
    def test_concurrent_template_rendering(self, template_service):
        """Test concurrent template rendering."""
        import threading
        import time
        
        template = template_service.get_template('business_letter')
        if not template:
            pytest.skip("Business letter template not available")
        
        # Prepare content
        content_data = {}
        for placeholder in template.placeholders:
            content_data[placeholder.key] = placeholder.placeholder_text
        
        results = []
        errors = []
        
        def render_template():
            try:
                result = template_service.render_template('business_letter', content_data)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=render_template)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert all(result is not None for result in results)
        
        # Should complete within reasonable time
        total_time = end_time - start_time
        assert total_time < 5.0