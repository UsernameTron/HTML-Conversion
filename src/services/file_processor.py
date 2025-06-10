"""File processing service with security and validation."""

import base64
import logging
import time
from io import BytesIO
from PIL import Image
from typing import Tuple, Optional
from utils.sanitizers import HTMLSanitizer, ContentValidator
from utils.validators import FileValidator, TextValidator
from models.style_models import SecurityConfig
from services.document_processors.pdf_processor import PDFProcessor
from services.document_processors.docx_processor import DOCXProcessor
from utils.cache_manager import StreamlitCacheManager, generate_content_hash
from utils.logger import get_enhanced_logger, log_performance
from utils.performance_monitor import get_performance_monitor, monitor_performance

logger = logging.getLogger(__name__)


class FileProcessor:
    """Secure file processor with validation and sanitization."""
    
    def __init__(self, sanitizer: Optional[HTMLSanitizer] = None, validator: Optional[FileValidator] = None):
        """Initialize file processor with dependencies."""
        self.sanitizer = sanitizer or HTMLSanitizer()
        self.file_validator = validator or FileValidator()  # Changed from validator to file_validator
        self.content_validator = ContentValidator()
        self.text_validator = TextValidator()  # Add text validator
        
        # Initialize document processors
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        
        # Initialize performance monitoring and caching
        self.cache_manager = StreamlitCacheManager()
        self.logger = get_enhanced_logger(__name__)
        self.performance_monitor = get_performance_monitor()
    
    @monitor_performance("file_processing")
    @log_performance("file_processing")
    def process_file(self, uploaded_file) -> dict:
        """
        Process uploaded file with security validation and caching.
        
        Args:
            uploaded_file: Streamlit uploaded file object or file path string
            
        Returns:
            Dictionary with success status and result content or error message
        """
        start_time = time.time()
        
        try:
            # Handle string file paths (for testing)
            if isinstance(uploaded_file, str):
                import os
                from pathlib import Path
                
                if not os.path.exists(uploaded_file):
                    return {
                        'success': False,
                        'error': f"File not found: {uploaded_file}"
                    }
                
                # Create a mock file info for string paths
                file_path = Path(uploaded_file)
                file_info = {
                    'filename': file_path.name,
                    'size': os.path.getsize(uploaded_file),
                    'extension': file_path.suffix.lower().lstrip('.'),
                    'category': self._get_file_category(file_path.suffix.lower().lstrip('.'))
                }
                
                # Open and read the file
                with open(uploaded_file, 'rb') as f:
                    success, result = self._process_file_content(f, file_info)
                    return {
                        'success': success,
                        'content' if success else 'error': result
                    }
            
            # Handle file objects (normal operation)
            else:
                # Get file information and validate
                is_valid, validation_error, file_info = self.file_validator.validate_file(uploaded_file)
                if not is_valid or file_info is None:
                    return {
                        'success': False,
                        'error': f"File validation failed: {validation_error or 'Unknown validation error'}"
                    }
                
                success, result = self._process_file_content(uploaded_file, file_info)
                return {
                    'success': success,
                    'content' if success else 'error': result
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"File processing error: {str(e)}",
                filename=getattr(uploaded_file, 'name', str(uploaded_file)),
                processing_time=processing_time,
                error_type=type(e).__name__
            )
            return {
                'success': False,
                'error': f"Error processing file: {str(e)}"
            }

    def _get_file_category(self, extension: str) -> str:
        """Get file category from extension."""
        text_extensions = ['txt', 'md', 'html', 'htm', 'css', 'js', 'json', 'csv']
        image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        document_extensions = ['pdf', 'docx', 'doc']
        
        if extension in text_extensions:
            return 'text'
        elif extension in image_extensions:
            return 'images'
        elif extension in document_extensions:
            return 'documents'
        else:
            return 'unknown'

    def _process_file_content(self, uploaded_file, file_info: dict) -> Tuple[bool, str]:
        """
        Process uploaded file with security validation and caching.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_info: File information dictionary
            
        Returns:
            Tuple of (success, result_content_or_error_message)
        """
        start_time = time.time()
        
        try:
            # Generate cache key from file content
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            file_hash = generate_content_hash(file_content)
            uploaded_file.seek(0)  # Reset for processing
            
            # Check cache first
            cached_result = self.cache_manager.get_cached_file_content(file_hash)
            if cached_result:
                self.logger.info(
                    "File processing cache hit",
                    filename=file_info['filename'],
                    file_hash=file_hash,
                    cache_hit=True
                )
                return True, cached_result
            
            # Process based on file category
            category = file_info['category']
            
            if category == 'text':
                success, result = self._process_text_file(uploaded_file, file_info)
            elif category == 'images':
                success, result = self._process_image_file(uploaded_file, file_info)
            elif category == 'documents':
                success, result = self._process_document_file(uploaded_file, file_info)
            else:
                return False, f"Unsupported file category: {category}"
            
            # Cache successful results
            if success and result:
                self.cache_manager.cache_file_content(file_hash, result, ttl=1800)  # 30 minutes
            
            # Log processing metrics
            processing_time = time.time() - start_time
            self.performance_monitor.record_file_processing(
                file_info['extension'], 
                file_info['size'], 
                processing_time
            )
            
            self.logger.file_processing_event(
                filename=file_info['filename'],
                operation=f"process_{category}",
                result="success" if success else "failure",
                file_size=file_info['size'],
                processing_time=processing_time,
                file_type=file_info['extension']
            )
            
            return success, result
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"File processing error: {str(e)}",
                filename=getattr(uploaded_file, 'name', str(uploaded_file)),
                processing_time=processing_time,
                error_type=type(e).__name__
            )
            return False, f"Error processing file: {str(e)}"

    def _detect_file_type(self, filename: str) -> str:
        """Detect specific file type based on extension."""
        from pathlib import Path
        ext = Path(filename).suffix.lower().lstrip('.')
        
        # Return specific file types as expected by tests
        type_mapping = {
            'txt': 'text',
            'md': 'text', 
            'html': 'text',
            'htm': 'text',
            'css': 'text',
            'js': 'text',
            'json': 'text',
            'csv': 'text',
            'png': 'image',
            'jpg': 'image', 
            'jpeg': 'image',
            'gif': 'image',
            'bmp': 'image',
            'webp': 'image',
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'doc'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def _process_text_file(self, file_obj, file_info: dict) -> Tuple[bool, str]:
        """Process text-based files."""
        try:
            # Read and decode content
            content = file_obj.read().decode('utf-8')
            
            # Validate text content
            is_valid, error_msg = self.text_validator.validate_text_input(content)
            if not is_valid:
                return False, error_msg or "Text validation failed"
            
            # Convert to HTML based on file type
            if file_info['extension'] in ['html', 'htm']:
                # HTML file - sanitize content
                sanitized_content = self.sanitizer.sanitize(content)
                return True, sanitized_content
            
            elif file_info['extension'] == 'md':
                # Markdown - convert to HTML (simplified)
                html_content = self._markdown_to_html(content)
                sanitized_content = self.sanitizer.sanitize(html_content)
                return True, sanitized_content
            
            elif file_info['extension'] == 'json':
                # JSON - format as code block
                html_content = f'<pre><code>{content}</code></pre>'
                return True, html_content
            
            elif file_info['extension'] in ['css', 'js']:
                # Code files - format as code block
                html_content = f'<pre><code class="{file_info["extension"]}">{content}</code></pre>'
                return True, html_content
            
            else:
                # Plain text - convert to paragraphs
                paragraphs = content.split('\\n\\n')
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                html_content = '\\n'.join([f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs])
                sanitized_content = self.sanitizer.sanitize(html_content)
                return True, sanitized_content
                
        except UnicodeDecodeError:
            return False, "File encoding not supported. Please use UTF-8."
        except Exception as e:
            logger.error(f"Text file processing error: {str(e)}")
            return False, f"Error processing text file: {str(e)}"
    
    def _process_image_file(self, file_obj, file_info: dict) -> Tuple[bool, str]:
        """Process image files."""
        try:
            # Validate image
            image = Image.open(file_obj)
            
            # Security checks
            if image.size[0] > 5000 or image.size[1] > 5000:
                return False, "Image too large (max 5000x5000 pixels)"
            
            # Convert to PNG for consistency and security
            buffered = BytesIO()
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ['RGBA', 'P']:
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            image.save(buffered, format="PNG", optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create secure HTML with proper attributes
            html_content = f'''<div style="text-align: center; margin: 20px 0;">
    <img src="data:image/png;base64,{img_str}" 
         alt="{file_info['filename']}" 
         style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" 
         loading="lazy">
    <p style="margin-top: 10px; font-size: 14px; color: #666; font-style: italic;">{file_info['filename']}</p>
</div>'''
            
            logger.info(f"Image processed: {file_info['filename']} ({image.size[0]}x{image.size[1]})")
            return True, html_content
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return False, f"Error processing image: {str(e)}"
    
    def _process_document_file(self, file_obj, file_info: dict) -> Tuple[bool, str]:
        """Process document files with real text extraction."""
        try:
            filename = file_info['filename']
            extension = file_info['extension']
            
            # Reset file pointer
            file_obj.seek(0)
            
            if extension == 'pdf':
                # Use PDF processor for real text extraction
                success, content = self.pdf_processor.extract_text_from_pdf(file_obj, filename)
                return success, content
                
            elif extension in ['docx', 'doc']:
                # Use DOCX processor for real text extraction
                if extension == 'docx':
                    success, content = self.docx_processor.extract_text_from_docx(file_obj, filename)
                    return success, content
                else:
                    # .doc files need conversion placeholder
                    return True, self._create_doc_conversion_placeholder(filename, file_info['size'])
            else:
                # Unsupported document type
                return True, self._create_unsupported_placeholder(filename, file_info)
                
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return False, f"Error processing document: {str(e)}"
    
    def _create_doc_conversion_placeholder(self, filename: str, file_size: int) -> str:
        """Create placeholder for .doc files that need conversion."""
        file_size_kb = file_size / 1024
        
        return f'''<div style="border: 2px solid #3182ce; border-radius: 12px; padding: 30px; margin: 20px 0; 
                   background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📝</div>
    <h2 style="color: #2c5282; margin-bottom: 10px; font-size: 24px;">Legacy Word Document</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{filename}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3182ce;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Size:</strong> {file_size_kb:.1f} KB</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Format:</strong> Legacy Microsoft Word (.doc)</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Status:</strong> Conversion required</p>
    </div>
    <div style="background: #ebf8ff; padding: 15px; border-radius: 8px; border: 1px solid #3182ce;">
        <p style="color: #2c5282; font-size: 14px; line-height: 1.5; margin: 0;">
            <strong>💡 Recommended Action:</strong><br>
            • Open the file in Microsoft Word<br>
            • Save as .docx format (newer format)<br>
            • Upload the .docx version for text extraction<br>
            • Or copy and paste content manually
        </p>
    </div>
</div>'''
    
    def _create_unsupported_placeholder(self, filename: str, file_info: dict) -> str:
        """Create placeholder for unsupported document types."""
        file_size_kb = file_info['size'] / 1024
        
        return f'''<div style="border: 2px dashed #a0aec0; border-radius: 12px; padding: 30px; margin: 20px 0; 
                   background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
    <h2 style="color: #4a5568; margin-bottom: 10px; font-size: 24px;">Unsupported Document</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{filename}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #a0aec0;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Type:</strong> {file_info['extension'].upper()}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Size:</strong> {file_size_kb:.1f} KB</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Status:</strong> Format not supported</p>
    </div>
    <p style="color: #718096; font-size: 14px; line-height: 1.5; margin-bottom: 0;">
        This document format cannot be processed automatically.<br>
        Consider converting to PDF or DOCX format for text extraction.
    </p>
</div>'''
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Simple markdown to HTML conversion (basic implementation)."""
        html_lines = []
        lines = markdown_content.split('\\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                html_lines.append('<br>')
                continue
            
            # Headers
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('#### '):
                html_lines.append(f'<h4>{line[5:]}</h4>')
            elif line.startswith('##### '):
                html_lines.append(f'<h5>{line[6:]}</h5>')
            elif line.startswith('###### '):
                html_lines.append(f'<h6>{line[7:]}</h6>')
            
            # Bold and italic (simple patterns)
            elif '**' in line or '*' in line:
                # Simple bold/italic replacement
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                line = line.replace('*', '<em>', 1).replace('*', '</em>', 1)
                html_lines.append(f'<p>{line}</p>')
            
            # Code blocks
            elif line.startswith('```'):
                html_lines.append('<pre><code>')
            elif line.endswith('```'):
                html_lines.append('</code></pre>')
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                html_lines.append(f'<li>{line[2:]}</li>')
            elif line.startswith('1. '):
                html_lines.append(f'<li>{line[3:]}</li>')
            
            # Regular paragraphs
            else:
                html_lines.append(f'<p>{line}</p>')
        
        return '\\n'.join(html_lines)