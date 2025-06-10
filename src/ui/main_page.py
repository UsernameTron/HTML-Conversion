"""Main application page with improved architecture."""

import streamlit as st
import logging
from typing import Optional
from models.style_models import StyleConfig, SecurityConfig
from services.file_processor import FileProcessor
from services.html_generator import HTMLGenerator
from utils.sanitizers import HTMLSanitizer, ContentValidator
from utils.validators import FileValidator, TextValidator
from ui.components.style_sidebar import StyleSidebar
from ui.components.file_uploader import FileUploaderComponent
from ui.components.preview import PreviewComponent
from ui.components.performance_dashboard import PerformanceDashboard

logger = logging.getLogger(__name__)


class MainPage:
    """Main application page with improved security and architecture."""
    
    def __init__(self):
        """Initialize main page with all dependencies."""
        # Initialize security components
        self.security_config = SecurityConfig()
        self.sanitizer = HTMLSanitizer(self.security_config)
        self.content_validator = ContentValidator(self.security_config)
        self.file_validator = FileValidator()
        self.text_validator = TextValidator()
        
        # Initialize services
        self.file_processor = FileProcessor(self.sanitizer, self.file_validator)
        
        # Initialize UI components
        self.style_sidebar = StyleSidebar()
        self.file_uploader = FileUploaderComponent(self.file_processor)
        self.preview_component = PreviewComponent()
        self.performance_dashboard = PerformanceDashboard()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables."""
        if 'style_config' not in st.session_state:
            st.session_state.style_config = StyleConfig()
        if 'processed_content' not in st.session_state:
            st.session_state.processed_content = ""
        if 'last_error' not in st.session_state:
            st.session_state.last_error = None
    
    def render(self):
        """Render the main page."""
        try:
            self._render_header()
            self._render_main_content()
        except Exception as e:
            logger.error(f"Main page rendering error: {str(e)}")
            st.error("An error occurred while loading the application. Please refresh the page.")
            if st.checkbox("Show technical details"):
                st.exception(e)
    
    def _render_header(self):
        """Render the application header."""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem; 
            border-radius: 20px; 
            color: white; 
            text-align: center;
            margin-bottom: 2rem; 
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
                pointer-events: none;
            "></div>
            <h1 style="
                font-family: 'Inter', sans-serif; 
                font-weight: 700; 
                font-size: 3rem; 
                margin-bottom: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                position: relative;
            ">
                🎨 HTML Text Formatter Pro
            </h1>
            <p style="
                font-family: 'Inter', sans-serif; 
                font-size: 1.2rem; 
                opacity: 0.95;
                position: relative;
                margin: 0;
            ">
                Transform your text content into stunning, professional HTML documents with enterprise-grade security
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_main_content(self):
        """Render the main content area."""
        # Check if user wants to see performance dashboard
        if st.sidebar.button("📊 Performance Dashboard"):
            st.session_state.show_performance_dashboard = not st.session_state.get('show_performance_dashboard', False)
        
        # Show performance dashboard if requested
        if st.session_state.get('show_performance_dashboard', False):
            self.performance_dashboard.render_full_dashboard()
            return
        
        # Sidebar for styling controls
        style_config = self.style_sidebar.render()
        
        # Show performance metrics in sidebar
        self.performance_dashboard.render_sidebar_metrics()
        
        # Update session state
        st.session_state.style_config = style_config
        
        # Main content columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_input_section()
        
        with col2:
            self._render_preview_section()
    
    def _render_input_section(self):
        """Render the input section with security validation."""
        st.header("📝 Input & Content")
        
        # Text input with validation
        text_input = st.text_area(
            "Enter your text content:",
            height=200,
            placeholder="Paste your text content here or upload a file below...",
            help="Enter plain text or HTML content. All content will be automatically sanitized for security.",
            max_chars=self.security_config.max_text_length
        )
        
        # File uploader
        uploaded_content = self.file_uploader.render()
        
        # Process content with priority: uploaded file > text input
        if uploaded_content:
            self._process_content(uploaded_content, "uploaded file")
        elif text_input:
            self._process_content(text_input, "text input")
        else:
            st.session_state.processed_content = ""
            st.session_state.last_error = None
    
    def _process_content(self, content: str, source: str):
        """Process and validate content from any source."""
        try:
            # Validate text input
            is_valid, error_msg = self.text_validator.validate_text_input(content)
            if not is_valid:
                st.error(f"❌ **Content validation failed:** {error_msg}")
                st.session_state.processed_content = ""
                st.session_state.last_error = error_msg
                return
            
            # Check if content is HTML or plain text
            if self._is_html_content(content):
                # HTML content - sanitize directly
                sanitized_content = self.sanitizer.sanitize(content)
                if not sanitized_content.strip():
                    st.warning("⚠️ Content was filtered due to security restrictions")
                    st.session_state.processed_content = ""
                    return
            else:
                # Plain text - convert to HTML paragraphs
                html_content = self._convert_text_to_html(content)
                sanitized_content = self.sanitizer.sanitize(html_content)
            
            # Update session state
            st.session_state.processed_content = sanitized_content
            st.session_state.last_error = None
            
            # Show success message
            if source == "text input":
                st.success(f"✅ Text processed successfully ({len(sanitized_content):,} characters)")
            
        except Exception as e:
            logger.error(f"Content processing error: {str(e)}")
            st.error(f"❌ **Processing error:** {str(e)}")
            st.session_state.processed_content = ""
            st.session_state.last_error = str(e)
    
    def _render_preview_section(self):
        """Render the preview section with error handling."""
        st.header("👁️ Live Preview")
        
        if st.session_state.processed_content:
            try:
                # Show preview
                self.preview_component.render(
                    st.session_state.processed_content, 
                    st.session_state.style_config
                )
                
                # Generate complete HTML document
                html_generator = HTMLGenerator(st.session_state.style_config)
                html_document = html_generator.generate_html_document(st.session_state.processed_content)
                
                # Show HTML code and download options
                self._render_output_section(html_document)
                
            except Exception as e:
                logger.error(f"Preview rendering error: {str(e)}")
                st.error("❌ **Preview error:** Unable to generate preview")
                if st.checkbox("Show technical details", key="preview_debug"):
                    st.exception(e)
        else:
            self._render_empty_preview()
    
    def _render_empty_preview(self):
        """Render empty preview state."""
        if st.session_state.last_error:
            st.error(f"❌ **Last error:** {st.session_state.last_error}")
        
        st.markdown(
            '''<div style="
                border: 2px dashed #cbd5e0; 
                border-radius: 16px; 
                padding: 48px 24px; 
                text-align: center;
                background: linear-gradient(145deg, #f7fafc 0%, #edf2f7 100%);
                color: #718096;
                margin: 20px 0;
                min-height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            ">
                <div style="font-size: 64px; margin-bottom: 24px;">📝</div>
                <h3 style="margin: 0 0 12px 0; color: #4a5568; font-size: 24px;">Ready to Create</h3>
                <p style="margin: 0; font-size: 16px; line-height: 1.5; max-width: 400px;">
                    Enter text above or upload a file to see your beautifully formatted preview with enterprise-grade security
                </p>
            </div>''', 
            unsafe_allow_html=True
        )
    
    def _render_output_section(self, html_document: str):
        """Render the output section with HTML code and download."""
        st.header("💻 Generated HTML")
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Document Size", f"{len(html_document):,} chars")
        with col2:
            st.metric("Content Size", f"{len(st.session_state.processed_content):,} chars")
        with col3:
            st.metric("Compression", f"{len(html_document)/len(st.session_state.processed_content):.1f}x")
        
        # Show HTML code
        with st.expander("📄 View HTML Source Code", expanded=False):
            st.code(html_document, language='html', line_numbers=True)
        
        # Download and copy buttons
        col_download, col_copy, col_preview = st.columns(3)
        
        with col_download:
            st.download_button(
                label="📥 Download HTML",
                data=html_document,
                file_name="formatted-document.html",
                mime="text/html",
                help="Download the complete HTML document",
                use_container_width=True
            )
        
        with col_copy:
            if st.button("📋 Copy HTML", help="Copy HTML to clipboard", use_container_width=True):
                st.code(html_document, language='html')
                st.success("✅ HTML code displayed above - select and copy")
        
        with col_preview:
            if st.button("🔍 Preview in Browser", help="Open preview in new tab", use_container_width=True):
                # Create a data URL for preview
                import base64
                encoded = base64.b64encode(html_document.encode()).decode()
                data_url = f"data:text/html;base64,{encoded}"
                
                st.markdown(f"""
                <script>
                    window.open('{data_url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                st.success("✅ Preview opened in new tab")
    
    def _is_html_content(self, content: str) -> bool:
        """Check if content already contains HTML tags."""
        # More sophisticated HTML detection
        html_indicators = ['<html', '<head', '<body', '<div', '<p', '<h1', '<h2', '<h3', '<span', '<img', '<a']
        content_lower = content.lower()
        
        # Check for common HTML tags
        html_tag_count = sum(1 for indicator in html_indicators if indicator in content_lower)
        
        # Check for basic tag structure
        has_opening_closing = '<' in content and '>' in content
        
        # Consider it HTML if it has multiple HTML indicators or clear tag structure
        return html_tag_count >= 2 or (has_opening_closing and any(tag in content_lower for tag in ['<p>', '<div>', '<h1>', '<h2>']))
    
    def _convert_text_to_html(self, text: str) -> str:
        """Convert plain text to HTML with paragraph formatting."""
        # Split into paragraphs
        paragraphs = text.split('\\n\\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Convert to HTML paragraphs
        html_paragraphs = []
        for paragraph in paragraphs:
            # Replace single line breaks with <br> tags
            paragraph = paragraph.replace('\\n', '<br>')
            html_paragraphs.append(f'<p>{paragraph}</p>')
        
        return '\\n'.join(html_paragraphs)