"""Styling controls sidebar component."""

import streamlit as st
import json
from typing import Dict, Any
from models.style_models import StyleConfig
from config.constants import COLOR_SCHEMES, MATERIAL_COLORS, FONT_COMBINATIONS


class StyleSidebar:
    """Styling controls sidebar component."""
    
    def __init__(self):
        """Initialize sidebar component."""
        pass
    
    def render(self) -> StyleConfig:
        """Render the styling sidebar and return configuration."""
        with st.sidebar:
            st.header("🎨 Design Studio")
            
            # Load current config from session state
            current_config = st.session_state.get('style_config', StyleConfig())
            
            # Theme selection
            theme = st.selectbox("🌙 Theme Mode", ["Light", "Dark", "Auto"])
            
            # Color scheme selection
            color_scheme_name = st.selectbox(
                "🎨 Color Scheme", 
                list(COLOR_SCHEMES.keys())
            )
            selected_scheme = COLOR_SCHEMES[color_scheme_name]
            
            st.divider()
            
            # Typography section
            typography_config = self._render_typography_section(current_config)
            
            st.divider()
            
            # Color controls
            color_config = self._render_color_section(current_config, selected_scheme)
            
            st.divider()
            
            # Layout and spacing
            layout_config = self._render_layout_section(current_config)
            
            st.divider()
            
            # Advanced styling
            advanced_config = self._render_advanced_section(current_config)
            
            st.divider()
            
            # Action buttons
            self._render_action_buttons(current_config)
            
            # Combine all configurations
            try:
                return StyleConfig(
                    **typography_config,
                    **color_config,
                    **layout_config,
                    **advanced_config
                )
            except Exception as e:
                st.error(f"Configuration error: {str(e)}")
                return current_config
    
    def _render_typography_section(self, config: StyleConfig) -> Dict[str, Any]:
        """Render typography controls."""
        st.subheader("📝 Typography")
        
        font_family_name = st.selectbox(
            "Font Family", 
            list(FONT_COMBINATIONS.keys()),
            index=0,
            help="Choose from Google Fonts and system fonts"
        )
        font_family = FONT_COMBINATIONS[font_family_name]
        
        font_size = st.slider("Font Size (px)", 12, 72, config.font_size)
        font_weight = st.selectbox(
            "Font Weight", 
            ["300", "400", "500", "600", "700"], 
            index=1,
            help="Font weight affects text boldness"
        )
        line_height = st.slider("Line Height", 1.0, 3.0, config.line_height, 0.1)
        letter_spacing = st.slider("Letter Spacing (px)", -2, 5, config.letter_spacing)
        
        return {
            'font_family': font_family,
            'font_size': font_size,
            'font_weight': font_weight,
            'line_height': line_height,
            'letter_spacing': letter_spacing
        }
    
    def _render_color_section(self, config: StyleConfig, selected_scheme: Dict[str, str]) -> Dict[str, Any]:
        """Render color controls."""
        st.subheader("🎨 Colors")
        
        # Material Design color picker
        st.write("**Material Design Colors:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Text Color:")
            text_color_family = st.selectbox(
                "Family", 
                list(MATERIAL_COLORS.keys()), 
                key="text_color_family",
                help="Choose material design color family"
            )
            text_shade = st.selectbox(
                "Shade", 
                list(MATERIAL_COLORS[text_color_family].keys()), 
                index=7, 
                key="text_shade",
                help="Darker shades (higher numbers) for better readability"
            )
            text_color = MATERIAL_COLORS[text_color_family][text_shade]
        
        with col2:
            st.write("Background Color:")
            bg_color_family = st.selectbox(
                "Family", 
                list(MATERIAL_COLORS.keys()), 
                index=12, 
                key="bg_color_family"
            )
            bg_shade = st.selectbox(
                "Shade", 
                list(MATERIAL_COLORS[bg_color_family].keys()), 
                index=0, 
                key="bg_shade",
                help="Lighter shades (lower numbers) for backgrounds"
            )
            background_color = MATERIAL_COLORS[bg_color_family][bg_shade]
        
        # Custom color pickers with current values as defaults
        custom_text = st.color_picker("Custom Text Color", text_color)
        custom_bg = st.color_picker("Custom Background Color", background_color)
        accent_color = st.color_picker("Accent Color", selected_scheme.get('accent', '#4285f4'))
        
        # Use custom colors if different from material colors
        final_text_color = custom_text if custom_text != text_color else text_color
        final_bg_color = custom_bg if custom_bg != background_color else background_color
        
        # Color contrast check
        if self._check_color_contrast(final_text_color, final_bg_color):
            st.success("✅ Good color contrast")
        else:
            st.warning("⚠️ Low color contrast - consider adjusting")
        
        return {
            'text_color': final_text_color,
            'background_color': final_bg_color,
            'accent_color': accent_color
        }
    
    def _render_layout_section(self, config: StyleConfig) -> Dict[str, Any]:
        """Render layout and spacing controls."""
        st.subheader("📐 Layout & Spacing")
        
        text_align = st.selectbox(
            "Text Alignment", 
            ["left", "center", "right", "justify"],
            index=0,
            help="Choose text alignment for the document"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            margin = st.number_input("Margin (px)", 0, 100, config.margin, help="Space around the document")
            padding = st.number_input("Padding (px)", 0, 100, config.padding, help="Inner spacing within the document")
        with col2:
            border_radius = st.number_input("Border Radius (px)", 0, 50, config.border_radius, help="Rounded corners")
            max_width = st.number_input("Max Width (px)", 600, 1400, config.max_width, help="Maximum document width")
        
        return {
            'text_align': text_align,
            'margin': margin,
            'padding': padding,
            'border_radius': border_radius,
            'max_width': max_width
        }
    
    def _render_advanced_section(self, config: StyleConfig) -> Dict[str, Any]:
        """Render advanced styling options."""
        st.subheader("✨ Advanced Styling")
        
        add_shadows = st.checkbox("Add Shadows", config.add_shadows, help="Add depth with box shadows")
        add_gradients = st.checkbox("Add Gradients", config.add_gradients, help="Use gradient backgrounds")
        modern_typography = st.checkbox("Modern Typography Scale", config.modern_typography, help="Enhanced heading hierarchy")
        responsive_design = st.checkbox("Responsive Design", config.responsive_design, help="Mobile-friendly layouts")
        
        return {
            'add_shadows': add_shadows,
            'add_gradients': add_gradients,
            'modern_typography': modern_typography,
            'responsive_design': responsive_design
        }
    
    def _render_action_buttons(self, config: StyleConfig):
        """Render action buttons."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset", type="secondary", help="Reset all styles to defaults"):
                st.session_state.style_config = StyleConfig()
                st.rerun()
        
        with col2:
            if st.button("💾 Export", help="Export theme configuration"):
                theme_json = config.to_json()
                st.download_button(
                    "📥 Download JSON",
                    data=theme_json,
                    file_name="theme_config.json",
                    mime="application/json",
                    help="Download theme configuration as JSON file"
                )
    
    def _check_color_contrast(self, text_color: str, bg_color: str) -> bool:
        """Simple color contrast check."""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def luminance(rgb):
            r, g, b = [x/255.0 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
            return 0.2126*r + 0.7152*g + 0.0722*b
        
        try:
            text_rgb = hex_to_rgb(text_color)
            bg_rgb = hex_to_rgb(bg_color)
            
            text_lum = luminance(text_rgb)
            bg_lum = luminance(bg_rgb)
            
            # Calculate contrast ratio
            lighter = max(text_lum, bg_lum)
            darker = min(text_lum, bg_lum)
            contrast_ratio = (lighter + 0.05) / (darker + 0.05)
            
            # WCAG AA standard requires 4.5:1 for normal text
            return contrast_ratio >= 4.5
        except:
            return True  # Assume OK if calculation fails