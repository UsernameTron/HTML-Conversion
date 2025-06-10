"""HTML generation service with modern templates."""

import logging
import time
from typing import Dict, Any
from models.style_models import StyleConfig
from utils.cache_manager import StreamlitCacheManager, generate_content_hash, generate_style_hash
from utils.logger import get_enhanced_logger, log_performance
from utils.performance_monitor import monitor_performance

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Professional HTML document generator."""
    
    def __init__(self, style_config: StyleConfig):
        """Initialize generator with style configuration."""
        self.style_config = style_config
        self.cache_manager = StreamlitCacheManager()
        self.logger = get_enhanced_logger(__name__)
    
    def generate_css(self) -> str:
        """Public method to generate CSS styles (for test compatibility)."""
        return self._generate_css_styles()

    @monitor_performance("html_generation")
    @log_performance("html_generation")
    def generate_html_document(self, content: str) -> str:
        """
        Generate complete HTML document with modern styling and caching.
        
        Args:
            content: Sanitized HTML content
            
        Returns:
            Complete HTML document string
        """
        start_time = time.time()
        
        try:
            # Generate cache keys
            content_hash = generate_content_hash(content)
            style_hash = generate_style_hash(self.style_config)
            document_hash = generate_content_hash(f"{content_hash}_{style_hash}")
            
            # Check cache first
            cached_html = self.cache_manager.get_cached_html_output(document_hash)
            if cached_html:
                self.logger.info(
                    "HTML generation cache hit",
                    content_hash=content_hash,
                    style_hash=style_hash,
                    cache_hit=True
                )
                return cached_html
            
            # Generate CSS styles
            css_styles = self._generate_css_styles()
            # Add all required security headers as meta tags
            security_headers = [
                '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; style-src \'self\' \'unsafe-inline\' https://fonts.googleapis.com; font-src \'self\' https://fonts.gstatic.com; script-src \'self\' \'unsafe-inline\'; img-src \'self\' data: https:; connect-src \'self\';">',
                '<meta http-equiv="X-Content-Type-Options" content="nosniff">',
                '<meta http-equiv="X-Frame-Options" content="DENY">',
                '<meta http-equiv="X-XSS-Protection" content="1; mode=block">',
                '<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">',
                '<meta http-equiv="Permissions-Policy" content="ambient-light-sensor=(), battery=(), camera=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(), geolocation=(), gyroscope=(), layout-animations=(), legacy-image-formats=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), oversized-images=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), speaker-selection=(), sync-xhr=(), unoptimized-images=(), unsized-media=(), usb=(), screen-wake-lock=(), web-share=(), xr-spatial-tracking=()">'
            ]
            security_headers_str = '\n    '.join(security_headers)
            html_document = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <meta name=\"description\" content=\"Professional HTML document generated with HTML Formatter Pro\">
    <meta name=\"generator\" content=\"HTML Formatter Pro\">
    {security_headers_str}
    <title>Professional Document</title>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&family=Poppins:wght@300;400;500;600;700&display=swap\" rel=\"stylesheet\">
    <style>
        {css_styles}
    </style>
</head>
<body>
    <div class=\"document-container\">
        {content}
    </div>
    <!-- Performance and accessibility enhancements -->
    <script>
        {self._generate_javascript()}
    </script>
</body>
</html>"""
            
            # Cache the generated HTML
            self.cache_manager.cache_html_output(document_hash, html_document, ttl=3600)  # 1 hour
            
            # Log performance metrics
            generation_time = time.time() - start_time
            self.logger.info(
                "HTML document generated successfully",
                content_hash=content_hash,
                style_hash=style_hash,
                generation_time=generation_time,
                document_size=len(html_document)
            )
            
            return html_document
            
        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(
                f"HTML generation error: {str(e)}",
                generation_time=generation_time,
                error_type=type(e).__name__
            )
            # Return basic fallback
            return f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>Document</title>\n</head>\n<body>\n    {content}\n</body>\n</html>"
    
    def _generate_css_styles(self) -> str:
        """Generate CSS styles based on configuration."""
        # Shadow styles
        shadow_styles = """
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        """ if self.style_config.add_shadows else ""
        
        # Gradient background
        if self.style_config.add_gradients:
            gradient_bg = f"""
                background: linear-gradient(145deg, {self.style_config.background_color} 0%, {self._hex_to_rgba(self.style_config.background_color, 0.9)} 100%);
            """
        else:
            gradient_bg = f"background-color: {self.style_config.background_color};"
        
        # Typography scale
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
        """ if self.style_config.modern_typography else ""
        
        # Responsive styles
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
        """ if self.style_config.responsive_design else ""
        
        return f"""
        :root {{
            --text-color: {self.style_config.text_color};
            --background-color: {self.style_config.background_color};
            --accent-color: {self.style_config.accent_color};
            --base-font-size: {self.style_config.font_size}px;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {self.style_config.font_family};
            font-size: var(--base-font-size);
            font-weight: {self.style_config.font_weight};
            color: var(--text-color);
            {gradient_bg}
            text-align: {self.style_config.text_align};
            line-height: {self.style_config.line_height};
            letter-spacing: {self.style_config.letter_spacing}px;
            margin: {self.style_config.margin}px;
            padding: {self.style_config.padding}px;
            border-radius: {self.style_config.border_radius}px;
            max-width: {self.style_config.max_width}px;
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
            border-radius: {self.style_config.border_radius}px;
            {shadow_styles}
        }}
        
        {typography_scale}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            {shadow_styles}
            loading: lazy;
        }}
        
        .highlight {{
            background: linear-gradient(120deg, transparent 0%, {self._hex_to_rgba(self.style_config.accent_color, 0.2)} 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
        }}
        
        .callout {{
            background: {self._hex_to_rgba(self.style_config.accent_color, 0.1)};
            border: 1px solid {self._hex_to_rgba(self.style_config.accent_color, 0.3)};
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        ::selection {{
            background: {self._hex_to_rgba(self.style_config.accent_color, 0.3)};
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
                font-size: 12pt;
                line-height: 1.4;
            }}
            .document-container {{
                box-shadow: none;
                padding: 0;
            }}
            img {{
                max-width: 100%;
                page-break-inside: avoid;
            }}
        }}
        
        /* Accessibility improvements */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --text-color: #e2e8f0;
                --background-color: #1a202c;
            }}
        }}
        """
    
    def _generate_javascript(self) -> str:
        """Generate minimal JavaScript for enhancements."""
        return """
        // Smooth loading animation
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.opacity = '0';
            document.body.style.transform = 'translateY(20px)';
            
            setTimeout(function() {
                document.body.style.transition = 'all 0.6s ease';
                document.body.style.opacity = '1';
                document.body.style.transform = 'translateY(0)';
            }, 100);
        });
        
        // Image lazy loading fallback
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Security: Remove any potentially dangerous scripts
        document.querySelectorAll('script').forEach(script => {
            if (script.src && !script.src.startsWith(window.location.origin)) {
                script.remove();
            }
        });
        """
    
    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> str:
        """Convert hex color to rgba with alpha."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"rgba({r}, {g}, {b}, {alpha})"
        return hex_color