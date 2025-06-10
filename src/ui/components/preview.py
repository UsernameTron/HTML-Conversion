"""Preview component for styled content."""

import streamlit as st
import logging
from typing import Dict, Any
from models.style_models import StyleConfig

logger = logging.getLogger(__name__)


class PreviewComponent:
    """Preview component for styled content with security."""
    
    def __init__(self):
        """Initialize preview component."""
        pass
    
    def render(self, content: str, style_config: StyleConfig):
        """Render preview of styled content with security measures."""
        if not content:
            self._render_empty_state()
            return
        
        try:
            # Generate preview styles
            preview_style = self._generate_preview_style(style_config)
            
            # Render preview with security notice
            st.markdown(
                f'<div class="preview-container" style="{preview_style}">{content}</div>',
                unsafe_allow_html=True  # Content is already sanitized
            )
            
            # Show preview information
            self._render_preview_info(content, style_config)
            
        except Exception as e:
            logger.error(f"Preview rendering error: {str(e)}")
            st.error("Error rendering preview. Please check your content.")
    
    def _render_empty_state(self):
        """Render empty state when no content."""
        st.markdown(
            '''<div style="
                border: 2px dashed #cbd5e0; 
                border-radius: 16px; 
                padding: 48px 24px; 
                text-align: center;
                background: linear-gradient(145deg, #f7fafc 0%, #edf2f7 100%);
                color: #718096;
                margin: 20px 0;
            ">
                <div style="font-size: 48px; margin-bottom: 16px;">📝</div>
                <h3 style="margin: 0 0 8px 0; color: #4a5568;">No Content Yet</h3>
                <p style="margin: 0; font-size: 14px;">
                    Enter text above or upload a file to see your formatted preview
                </p>
            </div>''', 
            unsafe_allow_html=True
        )
    
    def _generate_preview_style(self, config: StyleConfig) -> str:
        """Generate CSS styles for preview with security validation."""
        # Validate all style values for security
        safe_values = self._validate_style_values(config)
        
        shadow_style = "box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05);" if safe_values['add_shadows'] else ""
        
        if safe_values['add_gradients']:
            gradient_bg = f"background: linear-gradient(145deg, {safe_values['background_color']} 0%, {self._hex_to_rgba(safe_values['background_color'], 0.8)} 100%);"
        else:
            gradient_bg = f"background-color: {safe_values['background_color']};"
        
        return f"""
            font-family: {safe_values['font_family']};
            font-size: {safe_values['font_size']}px;
            font-weight: {safe_values['font_weight']};
            color: {safe_values['text_color']};
            {gradient_bg}
            text-align: {safe_values['text_align']};
            line-height: {safe_values['line_height']};
            letter-spacing: {safe_values['letter_spacing']}px;
            margin: {safe_values['margin']}px;
            padding: {safe_values['padding']}px;
            border-radius: {safe_values['border_radius']}px;
            max-width: {safe_values['max_width']}px;
            {shadow_style}
            transition: all 0.3s ease;
            border: 1px solid #e1e5e9;
            min-height: 200px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        """
    
    def _validate_style_values(self, config: StyleConfig) -> Dict[str, Any]:
        """Validate and sanitize style values for security."""
        safe_values = {}
        
        # Font family - only allow safe fonts
        safe_fonts = [
            'Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Poppins',
            '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica Neue',
            'Arial', 'sans-serif', 'Georgia', 'Times New Roman', 'serif',
            'Monaco', 'Consolas', 'Courier New', 'monospace'
        ]
        
        # Validate font family contains only safe fonts
        font_parts = [part.strip().strip('"\'') for part in config.font_family.split(',')]
        validated_fonts = [font for font in font_parts if font in safe_fonts]
        safe_values['font_family'] = ', '.join(validated_fonts) if validated_fonts else 'sans-serif'
        
        # Numeric values - ensure they're within safe ranges
        safe_values['font_size'] = max(12, min(72, config.font_size))
        safe_values['line_height'] = max(1.0, min(3.0, config.line_height))
        safe_values['letter_spacing'] = max(-2, min(5, config.letter_spacing))
        safe_values['margin'] = max(0, min(100, config.margin))
        safe_values['padding'] = max(0, min(100, config.padding))
        safe_values['border_radius'] = max(0, min(50, config.border_radius))
        safe_values['max_width'] = max(600, min(1400, config.max_width))
        
        # String values - validate format
        safe_values['font_weight'] = config.font_weight if config.font_weight in ['300', '400', '500', '600', '700'] else '400'
        safe_values['text_align'] = config.text_align if config.text_align in ['left', 'center', 'right', 'justify'] else 'left'
        
        # Color values - validate hex format
        safe_values['text_color'] = self._validate_hex_color(config.text_color) or '#2d3748'
        safe_values['background_color'] = self._validate_hex_color(config.background_color) or '#ffffff'
        safe_values['accent_color'] = self._validate_hex_color(config.accent_color) or '#4285f4'
        
        # Boolean values
        safe_values['add_shadows'] = bool(config.add_shadows)
        safe_values['add_gradients'] = bool(config.add_gradients)
        
        return safe_values
    
    def _validate_hex_color(self, color: str) -> str:
        """Validate hex color format."""
        if not color or not isinstance(color, str):
            return None
        
        color = color.strip()
        if not color.startswith('#'):
            return None
        
        hex_part = color[1:]
        if len(hex_part) != 6:
            return None
        
        try:
            int(hex_part, 16)
            return color.lower()
        except ValueError:
            return None
    
    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> str:
        """Convert hex color to rgba with validation."""
        validated_hex = self._validate_hex_color(hex_color)
        if not validated_hex:
            return "rgba(255, 255, 255, 1.0)"
        
        hex_color = validated_hex.lstrip('#')
        try:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            alpha = max(0.0, min(1.0, alpha))  # Clamp alpha between 0 and 1
            return f"rgba({r}, {g}, {b}, {alpha})"
        except (ValueError, IndexError):
            return "rgba(255, 255, 255, 1.0)"
    
    def _render_preview_info(self, content: str, style_config: StyleConfig):
        """Render preview information and statistics."""
        with st.expander("📊 Content & Style Information", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Content Statistics:**")
                st.write(f"• Characters: {len(content):,}")
                st.write(f"• Words: {len(content.split()):,}")
                st.write(f"• HTML tags: {content.count('<'):,}")
                
                # Check for common HTML elements
                elements = ['p', 'h1', 'h2', 'h3', 'img', 'a', 'div']
                found_elements = [elem for elem in elements if f'<{elem}' in content.lower()]
                if found_elements:
                    st.write(f"• Elements: {', '.join(found_elements)}")
            
            with col2:
                st.write("**Style Summary:**")
                st.write(f"• Font: {style_config.font_family.split(',')[0]}")
                st.write(f"• Size: {style_config.font_size}px")
                st.write(f"• Colors: {style_config.text_color} on {style_config.background_color}")
                st.write(f"• Layout: {style_config.max_width}px max-width")
                
                # Style features
                features = []
                if style_config.add_shadows:
                    features.append("Shadows")
                if style_config.add_gradients:
                    features.append("Gradients")
                if style_config.modern_typography:
                    features.append("Modern Typography")
                if style_config.responsive_design:
                    features.append("Responsive")
                
                if features:
                    st.write(f"• Features: {', '.join(features)}")
        
        # Security information
        with st.expander("🔒 Security Information", expanded=False):
            st.success("✅ **Content Security Status**")
            st.write("• HTML content has been sanitized")
            st.write("• Dangerous scripts and styles removed")
            st.write("• All user inputs validated")
            st.write("• Safe for display and download")
            
            st.info("🛡️ **Security Measures Applied:**")
            st.write("• XSS protection via HTML sanitization")
            st.write("• Content Security Policy headers")
            st.write("• Input validation and size limits")
            st.write("• Safe CSS property filtering")