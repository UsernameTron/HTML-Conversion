import streamlit as st
import base64
from io import BytesIO
import pandas as pd
from PIL import Image
import json
import colorsys

# Page configuration
st.set_page_config(
    page_title="HTML Text Formatter Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Material Design Color Palette
MATERIAL_COLORS = {
    'Red': {
        '50': '#ffebee', '100': '#ffcdd2', '200': '#ef9a9a', '300': '#e57373',
        '400': '#ef5350', '500': '#f44336', '600': '#e53935', '700': '#d32f2f',
        '800': '#c62828', '900': '#b71c1c'
    },
    'Pink': {
        '50': '#fce4ec', '100': '#f8bbd9', '200': '#f48fb1', '300': '#f06292',
        '400': '#ec407a', '500': '#e91e63', '600': '#d81b60', '700': '#c2185b',
        '800': '#ad1457', '900': '#880e4f'
    },
    'Purple': {
        '50': '#f3e5f5', '100': '#e1bee7', '200': '#ce93d8', '300': '#ba68c8',
        '400': '#ab47bc', '500': '#9c27b0', '600': '#8e24aa', '700': '#7b1fa2',
        '800': '#6a1b9a', '900': '#4a148c'
    },
    'Deep Purple': {
        '50': '#ede7f6', '100': '#d1c4e9', '200': '#b39ddb', '300': '#9575cd',
        '400': '#7e57c2', '500': '#673ab7', '600': '#5e35b1', '700': '#512da8',
        '800': '#4527a0', '900': '#311b92'
    },
    'Indigo': {
        '50': '#e8eaf6', '100': '#c5cae9', '200': '#9fa8da', '300': '#7986cb',
        '400': '#5c6bc0', '500': '#3f51b5', '600': '#3949ab', '700': '#303f9f',
        '800': '#283593', '900': '#1a237e'
    },
    'Blue': {
        '50': '#e3f2fd', '100': '#bbdefb', '200': '#90caf9', '300': '#64b5f6',
        '400': '#42a5f5', '500': '#2196f3', '600': '#1e88e5', '700': '#1976d2',
        '800': '#1565c0', '900': '#0d47a1'
    },
    'Light Blue': {
        '50': '#e1f5fe', '100': '#b3e5fc', '200': '#81d4fa', '300': '#4fc3f7',
        '400': '#29b6f6', '500': '#03a9f4', '600': '#039be5', '700': '#0288d1',
        '800': '#0277bd', '900': '#01579b'
    },
    'Cyan': {
        '50': '#e0f2f1', '100': '#b2dfdb', '200': '#80cbc4', '300': '#4db6ac',
        '400': '#26a69a', '500': '#009688', '600': '#00897b', '700': '#00796b',
        '800': '#00695c', '900': '#004d40'
    },
    'Teal': {
        '50': '#e0f2f1', '100': '#b2dfdb', '200': '#80cbc4', '300': '#4db6ac',
        '400': '#26a69a', '500': '#009688', '600': '#00897b', '700': '#00796b',
        '800': '#00695c', '900': '#004d40'
    },
    'Green': {
        '50': '#e8f5e8', '100': '#c8e6c9', '200': '#a5d6a7', '300': '#81c784',
        '400': '#66bb6a', '500': '#4caf50', '600': '#43a047', '700': '#388e3c',
        '800': '#2e7d32', '900': '#1b5e20'
    },
    'Light Green': {
        '50': '#f1f8e9', '100': '#dcedc8', '200': '#c5e1a5', '300': '#aed581',
        '400': '#9ccc65', '500': '#8bc34a', '600': '#7cb342', '700': '#689f38',
        '800': '#558b2f', '900': '#33691e'
    },
    'Lime': {
        '50': '#f9fbe7', '100': '#f0f4c3', '200': '#e6ee9c', '300': '#dce775',
        '400': '#d4e157', '500': '#cddc39', '600': '#c0ca33', '700': '#afb42b',
        '800': '#9e9d24', '900': '#827717'
    },
    'Yellow': {
        '50': '#fffde7', '100': '#fff9c4', '200': '#fff59d', '300': '#fff176',
        '400': '#ffee58', '500': '#ffeb3b', '600': '#fdd835', '700': '#fbc02d',
        '800': '#f9a825', '900': '#f57f17'
    },
    'Amber': {
        '50': '#fff8e1', '100': '#ffecb3', '200': '#ffe082', '300': '#ffd54f',
        '400': '#ffca28', '500': '#ffc107', '600': '#ffb300', '700': '#ffa000',
        '800': '#ff8f00', '900': '#ff6f00'
    },
    'Orange': {
        '50': '#fff3e0', '100': '#ffe0b2', '200': '#ffcc80', '300': '#ffb74d',
        '400': '#ffa726', '500': '#ff9800', '600': '#fb8c00', '700': '#f57c00',
        '800': '#ef6c00', '900': '#e65100'
    },
    'Deep Orange': {
        '50': '#fbe9e7', '100': '#ffccbc', '200': '#ffab91', '300': '#ff8a65',
        '400': '#ff7043', '500': '#ff5722', '600': '#f4511e', '700': '#e64a19',
        '800': '#d84315', '900': '#bf360c'
    },
    'Brown': {
        '50': '#efebe9', '100': '#d7ccc8', '200': '#bcaaa4', '300': '#a1887f',
        '400': '#8d6e63', '500': '#795548', '600': '#6d4c41', '700': '#5d4037',
        '800': '#4e342e', '900': '#3e2723'
    },
    'Grey': {
        '50': '#fafafa', '100': '#f5f5f5', '200': '#eeeeee', '300': '#e0e0e0',
        '400': '#bdbdbd', '500': '#9e9e9e', '600': '#757575', '700': '#616161',
        '800': '#424242', '900': '#212121'
    },
    'Blue Grey': {
        '50': '#eceff1', '100': '#cfd8dc', '200': '#b0bec5', '300': '#90a4ae',
        '400': '#78909c', '500': '#607d8b', '600': '#546e7a', '700': '#455a64',
        '800': '#37474f', '900': '#263238'
    }
}

# Modern Color Schemes inspired by Google
COLOR_SCHEMES = {
    'Google Blue': {'primary': '#4285f4', 'secondary': '#1a73e8', 'accent': '#34a853'},
    'Google Red': {'primary': '#ea4335', 'secondary': '#d33b2c', 'accent': '#fbbc05'},
    'Google Green': {'primary': '#34a853', 'secondary': '#137333', 'accent': '#4285f4'},
    'Google Yellow': {'primary': '#fbbc05', 'secondary': '#f9ab00', 'accent': '#ea4335'},
    'Material Purple': {'primary': '#9c27b0', 'secondary': '#7b1fa2', 'accent': '#e91e63'},
    'Material Indigo': {'primary': '#3f51b5', 'secondary': '#303f9f', 'accent': '#2196f3'},
    'Material Teal': {'primary': '#009688', 'secondary': '#00796b', 'accent': '#4caf50'},
    'Material Orange': {'primary': '#ff9800', 'secondary': '#f57c00', 'accent': '#ff5722'},
    'Elegant Dark': {'primary': '#2c3e50', 'secondary': '#34495e', 'accent': '#3498db'},
    'Sunset': {'primary': '#ff6b6b', 'secondary': '#feca57', 'accent': '#48dbfb'},
    'Ocean': {'primary': '#0abde3', 'secondary': '#006ba6', 'accent': '#74b9ff'},
    'Forest': {'primary': '#00b894', 'secondary': '#00a085', 'accent': '#55a3ff'}
}

# Premium font combinations
FONT_COMBINATIONS = {
    'Google Fonts - Roboto': 'Roboto, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Open Sans': 'Open Sans, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Lato': 'Lato, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Montserrat': 'Montserrat, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Poppins': 'Poppins, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Inter': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    'Apple System': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'Modern Sans': '"Helvetica Neue", Helvetica, Arial, sans-serif',
    'Classic Serif': 'Georgia, "Times New Roman", Times, serif',
    'Code Mono': '"SF Mono", "Monaco", "Consolas", "Courier New", monospace'
}

# Custom CSS for sleek, modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%, #f093fb 200%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    .preview-container {
        border: 1px solid #e1e5e9;
        border-radius: 16px;
        padding: 24px;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        min-height: 200px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 20px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .preview-container:hover {
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1), 0 20px 40px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .html-code {
        background: linear-gradient(145deg, #f1f3f4 0%, #e8eaed 100%);
        border: 1px solid #dadce0;
        border-radius: 12px;
        padding: 20px;
        font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .color-picker-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .color-swatch {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 6px;
        margin: 2px;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .color-swatch:hover {
        transform: scale(1.1);
        border-color: #4285f4;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .success-message {
        background: linear-gradient(145deg, #e8f5e8 0%, #d4edda 100%);
        color: #155724;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 12px 0;
        font-weight: 500;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #dadce0;
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #4285f4 0%, #34a853 100%);
    }
    
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
        color: white;
        border-radius: 8px;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 4px rgba(66, 133, 244, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(66, 133, 244, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Dynamic header with color scheme
    st.markdown("""
    <div class="main-header">
        <h1>🎨 HTML Text Formatter Pro</h1>
        <p>Transform your text content into stunning, professional HTML documents with Google-inspired design</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar for styling controls
    with st.sidebar:
        st.header("🎨 Design Studio")
        
        # Theme selection with modern options
        theme = st.selectbox("🌙 Theme Mode", ["Light", "Dark", "Auto"])
        
        # Modern color schemes
        color_scheme_name = st.selectbox("🎨 Color Scheme", list(COLOR_SCHEMES.keys()))
        selected_scheme = COLOR_SCHEMES[color_scheme_name]
        
        st.divider()
        
        # Typography with Google Fonts
        st.subheader("📝 Typography")
        font_family_name = st.selectbox("Font Family", list(FONT_COMBINATIONS.keys()))
        font_family = FONT_COMBINATIONS[font_family_name]
        
        font_size = st.slider("Font Size (px)", 12, 72, 18)
        font_weight = st.selectbox("Font Weight", ["300", "400", "500", "600", "700"], index=1)
        line_height = st.slider("Line Height", 1.0, 3.0, 1.6, 0.1)
        letter_spacing = st.slider("Letter Spacing (px)", -2, 5, 0)
        
        st.divider()
        
        # Enhanced color controls
        st.subheader("🎨 Colors")
        
        # Quick color picker from Material Design
        st.write("**Material Design Colors:**")
        
        # Text color selection
        col1, col2 = st.columns(2)
        with col1:
            st.write("Text Color:")
            selected_text_color_family = st.selectbox("Color Family", list(MATERIAL_COLORS.keys()), key="text_color_family")
            selected_text_shade = st.selectbox("Shade", list(MATERIAL_COLORS[selected_text_color_family].keys()), index=7, key="text_shade")
            text_color = MATERIAL_COLORS[selected_text_color_family][selected_text_shade]
            
        with col2:
            st.write("Background Color:")
            selected_bg_color_family = st.selectbox("Color Family", list(MATERIAL_COLORS.keys()), index=12, key="bg_color_family")
            selected_bg_shade = st.selectbox("Shade", list(MATERIAL_COLORS[selected_bg_color_family].keys()), index=0, key="bg_shade")
            background_color = MATERIAL_COLORS[selected_bg_color_family][selected_bg_shade]
        
        # Custom color pickers as fallback
        custom_text = st.color_picker("Custom Text Color", text_color, key="custom_text")
        custom_bg = st.color_picker("Custom Background Color", background_color, key="custom_bg")
        
        # Use custom colors if they're different from material colors
        if custom_text != text_color:
            text_color = custom_text
        if custom_bg != background_color:
            background_color = custom_bg
            
        # Accent color for highlights
        accent_color = st.color_picker("Accent Color", selected_scheme['accent'])
        
        st.divider()
        
        # Layout and spacing
        st.subheader("📐 Layout & Spacing")
        text_align = st.selectbox("Text Alignment", ["left", "center", "right", "justify"])
        
        col1, col2 = st.columns(2)
        with col1:
            margin = st.number_input("Margin (px)", 0, 100, 24)
            padding = st.number_input("Padding (px)", 0, 100, 32)
        with col2:
            border_radius = st.number_input("Border Radius (px)", 0, 50, 8)
            max_width = st.number_input("Max Width (px)", 600, 1400, 900)
        
        st.divider()
        
        # Advanced styling
        st.subheader("✨ Advanced Styling")
        add_shadows = st.checkbox("Add Shadows", True)
        add_gradients = st.checkbox("Add Gradients", False)
        modern_typography = st.checkbox("Modern Typography Scale", True)
        responsive_design = st.checkbox("Responsive Design", True)
        
        st.divider()
        
        # Reset button
        if st.button("🔄 Reset All Styles", type="secondary"):
            st.rerun()
            
        # Export theme button
        theme_config = {
            'color_scheme': color_scheme_name,
            'font_family': font_family_name,
            'font_size': font_size,
            'text_color': text_color,
            'background_color': background_color,
            'accent_color': accent_color
        }
        
        if st.button("💾 Export Theme Config"):
            st.download_button(
                "Download Theme JSON",
                data=json.dumps(theme_config, indent=2),
                file_name="theme_config.json",
                mime="application/json"
            )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input & Content")
        
        # Text input
        text_input = st.text_area(
            "Enter your text content:",
            height=200,
            placeholder="Paste your text content here or upload a file below..."
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload File",
            type=['txt', 'md', 'csv', 'json', 'html', 'css', 'js', 'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Supports text files, images, PDF, and Word documents"
        )
        
        # Process uploaded file
        if uploaded_file is not None:
            file_type = uploaded_file.type
            file_name = uploaded_file.name.lower()
            
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            if file_type.startswith('text/') or any(file_name.endswith(ext) for ext in ['.txt', '.md', '.csv', '.json', '.html', '.css', '.js']):
                # Text-based files
                try:
                    text_content = uploaded_file.read().decode('utf-8')
                    text_input = text_content
                    st.success("✅ Text content loaded successfully")
                except:
                    st.error("❌ Could not read file as text")
                    
            elif file_type.startswith('image/'):
                # Image files
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
                
                # Convert image to base64 for HTML embedding
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                text_input = f"""<div style="text-align: center; margin: 20px 0;">
    <img src="data:image/png;base64,{img_str}" alt="{uploaded_file.name}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <p style="margin-top: 10px; font-size: 14px; color: #666; font-style: italic;">{uploaded_file.name}</p>
</div>"""
                st.success("🖼️ Image embedded as HTML")
                
            elif file_name.endswith('.pdf') or file_type == 'application/pdf':
                # PDF placeholder
                text_input = f"""<div style="border: 2px solid #e74c3c; border-radius: 12px; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📄</div>
    <h2 style="color: #c53030; margin-bottom: 10px; font-size: 24px;">PDF Document</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{uploaded_file.name}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #e74c3c;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Type:</strong> Portable Document Format</p>
    </div>
    <p style="color: #718096; font-size: 14px; line-height: 1.5; margin-bottom: 0;">
        PDF content cannot be directly displayed in this HTML formatter.<br>
        Consider extracting text content or providing a summary for HTML formatting.
    </p>
</div>"""
                st.warning("📄 PDF placeholder generated - extract text for formatting")
                
            elif any(file_name.endswith(ext) for ext in ['.docx', '.doc']) or file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
                # Word document placeholder
                text_input = f"""<div style="border: 2px solid #3182ce; border-radius: 12px; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📝</div>
    <h2 style="color: #2c5282; margin-bottom: 10px; font-size: 24px;">Word Document</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{uploaded_file.name}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3182ce;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Type:</strong> Microsoft Word Document</p>
    </div>
    <p style="color: #718096; font-size: 14px; line-height: 1.5; margin-bottom: 0;">
        Word document content cannot be directly parsed in this environment.<br>
        Copy and paste the text content from your document for HTML formatting.
    </p>
</div>"""
                st.warning("📝 DOCX placeholder generated - copy text content manually")
            else:
                # Unsupported file type
                text_input = f"""<div style="border: 2px dashed #a0aec0; border-radius: 12px; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📁</div>
    <h2 style="color: #4a5568; margin-bottom: 10px; font-size: 24px;">Unsupported File Format</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{uploaded_file.name}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #a0aec0;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Type:</strong> {file_type}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
    </div>
    <p style="color: #718096; font-size: 14px; line-height: 1.5; margin-bottom: 0;">
        This file type cannot be directly processed for HTML formatting.<br>
        Consider converting to a supported text format or manually entering content.
    </p>
</div>"""
                st.warning("⚠️ Unsupported format - placeholder generated")
    
    with col2:
        st.header("👁️ Live Preview")
        
        # Generate styled content
        if text_input:
            # Convert text to HTML paragraphs
            paragraphs = text_input.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            if not any('<' in p and '>' in p for p in paragraphs):
                # Plain text - convert to HTML paragraphs
                html_content = '\n    '.join([f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs])
            else:
                # Already contains HTML - use as is
                html_content = text_input
            
            # Apply enhanced styles for preview
            shadow_style = "box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05);" if add_shadows else ""
            gradient_bg = f"background: linear-gradient(145deg, {background_color} 0%, {hex_to_rgba(background_color, 0.8)} 100%);" if add_gradients else f"background-color: {background_color};"
            
            preview_style = f"""
            font-family: {font_family};
            font-size: {font_size}px;
            font-weight: {font_weight};
            color: {text_color};
            {gradient_bg}
            text-align: {text_align};
            line-height: {line_height};
            letter-spacing: {letter_spacing}px;
            margin: {margin}px;
            padding: {padding}px;
            border-radius: {border_radius}px;
            max-width: {max_width}px;
            {shadow_style}
            transition: all 0.3s ease;
            """
            
            # Show preview
            st.markdown(f'<div class="preview-container" style="{preview_style}">{html_content}</div>', unsafe_allow_html=True)
            
            # Generate enhanced HTML document
            html_document = generate_enhanced_html_document(html_content, {
                'font_family': font_family,
                'font_size': f"{font_size}px",
                'font_weight': font_weight,
                'text_color': text_color,
                'background_color': background_color,
                'accent_color': accent_color,
                'text_align': text_align,
                'line_height': str(line_height),
                'letter_spacing': f"{letter_spacing}px",
                'margin': f"{margin}px",
                'padding': f"{padding}px",
                'border_radius': f"{border_radius}px",
                'max_width': f"{max_width}px",
                'add_shadows': add_shadows,
                'add_gradients': add_gradients,
                'modern_typography': modern_typography,
                'responsive_design': responsive_design,
                'color_scheme': selected_scheme
            })
            
            st.header("💻 Generated HTML")
            
            # Show HTML code
            st.code(html_document, language='html')
            
            # Download and copy buttons
            col_download, col_copy = st.columns(2)
            
            with col_download:
                st.download_button(
                    label="📥 Download HTML",
                    data=html_document,
                    file_name="formatted-document.html",
                    mime="text/html"
                )
            
            with col_copy:
                if st.button("📋 Copy to Clipboard"):
                    st.code(html_document, language='html')
                    st.success("HTML code is displayed above - select and copy manually")
        
        else:
            st.markdown('<div class="preview-container">Your formatted text will appear here...</div>', unsafe_allow_html=True)

def hex_to_rgba(hex_color, alpha=1.0):
    """Convert hex color to rgba with alpha"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"
    return hex_color

def generate_enhanced_html_document(content, styles):
    # Modern CSS with Google-inspired design
    shadow_styles = """
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    """ if styles['add_shadows'] else ""
    
    gradient_bg = f"""
        background: linear-gradient(145deg, {styles['background_color']} 0%, {hex_to_rgba(styles['background_color'], 0.9)} 100%);
    """ if styles['add_gradients'] else f"background-color: {styles['background_color']};"
    
    typography_scale = """
        h1 { font-size: 2.5em; font-weight: 700; margin-bottom: 0.5em; color: var(--accent-color); }
        h2 { font-size: 2em; font-weight: 600; margin-bottom: 0.75em; }
        h3 { font-size: 1.5em; font-weight: 500; margin-bottom: 0.75em; }
        h4 { font-size: 1.25em; font-weight: 500; margin-bottom: 0.75em; }
        h5 { font-size: 1.1em; font-weight: 500; margin-bottom: 0.75em; }
        h6 { font-size: 1em; font-weight: 500; margin-bottom: 0.75em; }
        p { margin-bottom: 1.2em; }
        blockquote {
            border-left: 4px solid var(--accent-color);
            padding-left: 1.5em;
            margin: 1.5em 0;
            font-style: italic;
            background: rgba(0, 0, 0, 0.02);
            padding: 1em 1.5em;
            border-radius: 4px;
        }
        a {
            color: var(--accent-color);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.2s ease;
        }
        a:hover {
            border-bottom-color: var(--accent-color);
        }
        code {
            background: rgba(0, 0, 0, 0.05);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }
        pre {
            background: rgba(0, 0, 0, 0.05);
            padding: 1em;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1.5em 0;
        }
    """ if styles['modern_typography'] else ""
    
    responsive_styles = """
        @media (max-width: 768px) {
            body {
                padding: 1rem;
                font-size: calc(var(--base-font-size) * 0.9);
            }
            h1 { font-size: 2em; }
            h2 { font-size: 1.75em; }
            h3 { font-size: 1.5em; }
        }
        @media (max-width: 480px) {
            body {
                padding: 0.75rem;
                font-size: calc(var(--base-font-size) * 0.85);
            }
        }
    """ if styles['responsive_design'] else ""
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Document</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: {styles['color_scheme']['primary']};
            --secondary-color: {styles['color_scheme']['secondary']};
            --accent-color: {styles['accent_color']};
            --text-color: {styles['text_color']};
            --background-color: {styles['background_color']};
            --base-font-size: {styles['font_size']};
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {styles['font_family']};
            font-size: var(--base-font-size);
            font-weight: {styles['font_weight']};
            color: var(--text-color);
            {gradient_bg}
            text-align: {styles['text_align']};
            line-height: {styles['line_height']};
            letter-spacing: {styles['letter_spacing']};
            margin: {styles['margin']};
            padding: {styles['padding']};
            border-radius: {styles['border_radius']};
            max-width: {styles['max_width']};
            margin-left: auto;
            margin-right: auto;
            {shadow_styles}
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .document-container {{
            {gradient_bg}
            padding: 2rem;
            border-radius: {styles['border_radius']};
            {shadow_styles}
        }}
        
        {typography_scale}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            {shadow_styles}
        }}
        
        .highlight {{
            background: linear-gradient(120deg, transparent 0%, {hex_to_rgba(styles['accent_color'], 0.2)} 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
        }}
        
        .callout {{
            background: {hex_to_rgba(styles['accent_color'], 0.1)};
            border: 1px solid {hex_to_rgba(styles['accent_color'], 0.3)};
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        ::selection {{
            background: {hex_to_rgba(styles['accent_color'], 0.3)};
            color: white;
        }}
        
        {responsive_styles}
        
        /* Print styles */
        @media print {{
            body {{
                box-shadow: none;
                max-width: none;
                margin: 0;
                padding: 1cm;
            }}
        }}
    </style>
</head>
<body>
    <div class="document-container">
        {content}
    </div>
    
    <!-- Add subtle animation on load -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            document.body.style.opacity = '0';
            document.body.style.transform = 'translateY(20px)';
            
            setTimeout(function() {{
                document.body.style.transition = 'all 0.6s ease';
                document.body.style.opacity = '1';
                document.body.style.transform = 'translateY(0)';
            }}, 100);
        }});
    </script>
</body>
</html>"""

# Helper function to create color swatches
def create_color_swatch_html(color_dict):
    swatches = ""
    for color_name, shades in color_dict.items():
        for shade, hex_color in shades.items():
            swatches += f'<span class="color-swatch" style="background-color: {hex_color};" title="{color_name} {shade}"></span>'
    return swatches

if __name__ == "__main__":
    main()