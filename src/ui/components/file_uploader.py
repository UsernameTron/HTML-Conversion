"""File uploader component with validation and processing."""

import streamlit as st
import logging
from typing import Optional
from services.file_processor import FileProcessor
from config.constants import SUPPORTED_FILE_TYPES

logger = logging.getLogger(__name__)


class FileUploaderComponent:
    """File uploader component with validation and processing."""
    
    def __init__(self, file_processor: FileProcessor):
        """Initialize file uploader with processor."""
        self.file_processor = file_processor
    
    def render(self) -> Optional[str]:
        """Render file uploader and return processed content."""
        # Create list of allowed extensions
        all_extensions = []
        for category_exts in SUPPORTED_FILE_TYPES.values():
            all_extensions.extend(category_exts)
        
        uploaded_file = st.file_uploader(
            "📁 Upload File",
            type=all_extensions,
            help=self._get_help_text(),
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            return self._process_uploaded_file(uploaded_file)
        
        return None
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[str]:
        """Process the uploaded file and return content."""
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
        
        # Process file with progress indicator
        with st.spinner("🔄 Processing file..."):
            try:
                success, result = self.file_processor.process_file(uploaded_file)
                
                if success:
                    st.success("✅ File processed successfully!")
                    
                    # Show processing details in expander
                    with st.expander("📋 Processing Details", expanded=False):
                        st.write(f"**Original size:** {uploaded_file.size:,} bytes")
                        st.write(f"**File type:** {uploaded_file.type or 'Unknown'}")
                        st.write(f"**Content length:** {len(result):,} characters")
                    
                    return result
                else:
                    st.error(f"❌ **Processing failed:** {result}")
                    
                    # Show troubleshooting tips
                    with st.expander("🔧 Troubleshooting Tips"):
                        self._show_troubleshooting_tips(uploaded_file.name)
                    
                    return None
                    
            except Exception as e:
                logger.error(f"File processing error: {str(e)}")
                st.error(f"❌ **Unexpected error:** {str(e)}")
                return None
    
    def _get_help_text(self) -> str:
        """Generate help text for file uploader."""
        return """**Supported file types:**
        
**📝 Text Files:** txt, md, csv, json, html, css, js
**🖼️ Images:** png, jpg, jpeg, gif, bmp  
**📄 Documents:** pdf, docx, doc (placeholder generation)

**Security features:**
- ✅ File type validation
- ✅ Size limits (50MB max)
- ✅ Content sanitization
- ✅ Malware detection"""
    
    def _show_troubleshooting_tips(self, filename: str):
        """Show troubleshooting tips based on file type."""
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        st.write("**Common solutions:**")
        
        if file_ext in ['txt', 'md', 'csv', 'html', 'css', 'js']:
            st.write("• Ensure the file is valid UTF-8 encoded")
            st.write("• Check for special characters or null bytes")
            st.write("• Try reducing file size if very large")
        
        elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            st.write("• Ensure the image is not corrupted")
            st.write("• Try reducing image dimensions (max 5000x5000)")
            st.write("• Convert to PNG format for best compatibility")
        
        elif file_ext in ['pdf', 'docx', 'doc']:
            st.write("• Document processing generates placeholders only")
            st.write("• For text formatting, copy and paste content manually")
            st.write("• Future updates will include text extraction")
        
        else:
            st.write("• Check that the file extension is correct")
            st.write("• Ensure the file is not corrupted")
            st.write("• Try converting to a supported format")
        
        st.write("\\n**Security notes:**")
        st.write("• Files are scanned for security threats")
        st.write("• Content is automatically sanitized")
        st.write("• No data is stored permanently")


class FileTypeIcon:
    """Helper class for file type icons."""
    
    @staticmethod
    def get_icon(file_extension: str) -> str:
        """Get appropriate icon for file type."""
        icons = {
            'txt': '📄',
            'md': '📝',
            'csv': '📊',
            'json': '🔧',
            'html': '🌐',
            'css': '🎨',
            'js': '⚡',
            'pdf': '📕',
            'docx': '📘',
            'doc': '📘',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'gif': '🎞️',
            'bmp': '🖼️'
        }
        
        return icons.get(file_extension.lower(), '📁')