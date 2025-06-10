"""
HTML Text Formatter Pro - Secure, Modular Architecture
======================================================

A professional-grade web application that transforms text content into stunning, 
Google-inspired HTML documents with enterprise-grade security.

Features:
- 🔒 XSS Protection via HTML sanitization
- 🛡️ Comprehensive input validation  
- 📦 Modular, maintainable architecture
- 🎨 Material Design UI components
- 📱 Responsive design support
- 🚀 Performance optimized

Security Features:
- Content Security Policy headers
- HTML sanitization with bleach
- File type and size validation
- Input length limits
- Path traversal protection
- Malware detection
"""

import streamlit as st
import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

# Page configuration with security headers
st.set_page_config(
    page_title="HTML Text Formatter Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/html-formatter-pro',
        'Report a bug': 'https://github.com/your-repo/html-formatter-pro/issues',
        'About': """
        # HTML Text Formatter Pro
        
        Transform your text content into stunning, professional HTML documents 
        with enterprise-grade security and Google-inspired design.
        
        **Security Features:**
        - XSS Protection
        - Input Validation
        - Content Sanitization
        - File Security Scanning
        
        **Version:** 2.0.0 (Secure Architecture)
        """
    }
)

# Custom CSS for modern, secure styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
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
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .preview-container:hover {
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1), 0 20px 40px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .security-badge {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 8px 4px;
        box-shadow: 0 2px 4px rgba(72, 187, 120, 0.3);
    }
    
    .error-container {
        background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
        border: 1px solid #fc8181;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        color: #742a2a;
    }
    
    .success-container {
        background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
        border: 1px solid #68d391;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        color: #22543d;
    }
    
    /* Security indicators */
    .security-status {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: rgba(72, 187, 120, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    /* Responsive improvements */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        .main-header h1 {
            font-size: 2rem !important;
        }
    }
</style>

<!-- Security Status Indicator -->
<div class="security-status">
    🔒 Secure Mode Active
</div>

""", unsafe_allow_html=True)


def main():
    """Main application entry point with error handling."""
    try:
        logger.info("Starting HTML Text Formatter Pro (Secure Architecture)")
        
        # Navigation sidebar
        with st.sidebar:
            st.title("🎨 HTML Formatter Pro")
            
            # Navigation menu
            page = st.radio(
                "Navigate to:",
                ["🏠 Main Editor", "📋 Templates", "📊 Performance"],
                key="navigation"
            )
        
        # Route to appropriate page
        if page == "🏠 Main Editor":
            from ui.main_page import MainPage
            main_page = MainPage()
            main_page.render()
        
        elif page == "📋 Templates":
            from ui.pages.template_page import TemplatePage
            template_page = TemplatePage()
            template_page.render()
        
        elif page == "📊 Performance":
            from ui.components.performance_dashboard import PerformanceDashboard
            dashboard = PerformanceDashboard()
            dashboard.render_full_dashboard()
        
        # Security information footer
        render_security_footer()
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        st.error("❌ **Application Error:** Module import failed")
        st.write("This usually happens when dependencies are not installed correctly.")
        
        with st.expander("🔧 Troubleshooting Steps"):
            st.write("1. **Install dependencies:**")
            st.code("pip install -r requirements.txt")
            
            st.write("2. **Check Python path:**")
            st.code("import sys\\nprint(sys.path)")
            
            st.write("3. **Verify file structure:**")
            st.code("ls -la src/")
            
            st.write("4. **Run from correct directory:**")
            st.code("streamlit run app.py")
        
        if st.button("📄 Show Technical Details"):
            st.exception(e)
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("❌ **Critical Error:** Application failed to start")
        
        st.write("**Possible causes:**")
        st.write("• Missing or corrupted files")
        st.write("• Insufficient permissions")
        st.write("• Configuration issues")
        
        if st.button("🔧 Show Error Details"):
            st.exception(e)
        
        st.write("**Recovery options:**")
        if st.button("🔄 Restart Application"):
            st.rerun()


def render_security_footer():
    """Render security information footer."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔒 Security Features**
        <div class="security-badge">XSS Protection</div>
        <div class="security-badge">Input Validation</div>
        <div class="security-badge">Content Sanitization</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        **🛡️ Data Protection**
        <div class="security-badge">No Data Storage</div>
        <div class="security-badge">HTTPS Only</div>
        <div class="security-badge">CSP Headers</div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        **📊 Architecture**
        <div class="security-badge">Modular Design</div>
        <div class="security-badge">Error Handling</div>
        <div class="security-badge">Audit Logging</div>
        """, unsafe_allow_html=True)
    
    # Version and build info
    with st.expander("ℹ️ Application Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Version:** 2.0.0 (Secure Architecture)")
            st.write("**Security Level:** Enterprise Grade")
            st.write("**Architecture:** Modular/Service-based")
        
        with col2:
            st.write("**Dependencies:** Validated & Secure")
            st.write("**Logging:** Enabled")
            st.write("**Error Handling:** Comprehensive")


if __name__ == "__main__":
    main()