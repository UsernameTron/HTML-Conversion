"""Extended template library with additional creative, technical, and marketing templates."""

from models.template_models import Template, TemplateMetadata, ContentPlaceholder, TemplateCategory, StyleOverride


def add_creative_templates(template_service):
    """Add creative templates to the template service."""
    
    # Blog Post Template
    template = Template(
        id="blog_post",
        metadata=TemplateMetadata(
            name="Blog Post",
            description="Modern blog post with featured image and engaging layout",
            category=TemplateCategory.CREATIVE,
            tags=["blog", "post", "content", "writing"],
            difficulty_level="beginner",
            estimated_time="15 minutes"
        ),
        html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{post_title}}</title>
    <style>
        body { font-family: 'Georgia', serif; line-height: 1.8; margin: 0; color: #333; background: #fafafa; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 40px; }
        .post-title { font-size: 42px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; line-height: 1.2; }
        .post-meta { color: #7f8c8d; font-size: 16px; margin-bottom: 30px; }
        .author-info { display: flex; align-items: center; justify-content: center; gap: 15px; }
        .author-avatar { width: 50px; height: 50px; border-radius: 50%; background: #3498db; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
        .featured-image { width: 100%; height: 400px; object-fit: cover; border-radius: 12px; margin: 30px 0; }
        .post-content { font-size: 18px; line-height: 1.8; }
        .post-content h2 { color: #2c3e50; font-size: 28px; margin-top: 40px; margin-bottom: 20px; }
        .post-content h3 { color: #34495e; font-size: 22px; margin-top: 30px; margin-bottom: 15px; }
        .post-content p { margin-bottom: 20px; }
        .quote { background: #ecf0f1; border-left: 5px solid #3498db; padding: 20px; margin: 30px 0; font-style: italic; font-size: 20px; }
        .tags { margin-top: 40px; padding-top: 30px; border-top: 2px solid #ecf0f1; }
        .tag { display: inline-block; background: #3498db; color: white; padding: 5px 12px; margin: 5px; border-radius: 20px; font-size: 14px; text-decoration: none; }
        .footer { margin-top: 50px; padding-top: 30px; border-top: 2px solid #ecf0f1; text-align: center; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="post-title">{{post_title}}</h1>
            <div class="post-meta">
                <div class="author-info">
                    <div class="author-avatar">{{author_initial}}</div>
                    <div>
                        <div><strong>{{author_name}}</strong></div>
                        <div>{{publish_date}} • {{read_time}} min read</div>
                    </div>
                </div>
            </div>
        </div>
        
        <img src="{{featured_image_url}}" alt="{{featured_image_alt}}" class="featured-image">
        
        <div class="post-content">
            {{post_content}}
        </div>
        
        <div class="tags">
            <strong>Tags:</strong>
            {{post_tags}}
        </div>
        
        <div class="footer">
            <p>{{footer_text}}</p>
        </div>
    </div>
</body>
</html>
        """,
        placeholders=[
            ContentPlaceholder(key="post_title", label="Post Title", description="Title of the blog post", placeholder_text="The Future of Web Development"),
            ContentPlaceholder(key="author_name", label="Author Name", description="Name of the author", placeholder_text="Jane Smith"),
            ContentPlaceholder(key="author_initial", label="Author Initial", description="First letter of author's name", placeholder_text="J"),
            ContentPlaceholder(key="publish_date", label="Publish Date", description="Publication date", placeholder_text="December 9, 2024"),
            ContentPlaceholder(key="read_time", label="Read Time", description="Estimated reading time in minutes", placeholder_text="5"),
            ContentPlaceholder(key="featured_image_url", label="Featured Image URL", description="URL of the featured image", placeholder_text="https://via.placeholder.com/800x400"),
            ContentPlaceholder(key="featured_image_alt", label="Featured Image Alt Text", description="Alt text for the featured image", placeholder_text="Web development concept illustration"),
            ContentPlaceholder(key="post_content", label="Post Content", description="Main content of the blog post", placeholder_text="<p>Web development continues to evolve at a rapid pace...</p><h2>Key Trends</h2><p>Several trends are shaping the future...</p>", content_type="html"),
            ContentPlaceholder(key="post_tags", label="Post Tags", description="Tags for the post", placeholder_text="<span class='tag'>Web Development</span><span class='tag'>Technology</span><span class='tag'>Programming</span>", content_type="html"),
            ContentPlaceholder(key="footer_text", label="Footer Text", description="Footer message", placeholder_text="Thank you for reading! Follow me for more tech insights.")
        ]
    )
    template_service.template_library.add_template(template)
    
    # Newsletter Template
    template = Template(
        id="newsletter",
        metadata=TemplateMetadata(
            name="Email Newsletter",
            description="Professional email newsletter with sections and call-to-action",
            category=TemplateCategory.CREATIVE,
            tags=["newsletter", "email", "marketing", "communication"],
            difficulty_level="intermediate",
            estimated_time="25 minutes"
        ),
        html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{newsletter_title}}</title>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f4f4f4; }
        .newsletter { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
        .newsletter-title { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
        .newsletter-subtitle { font-size: 16px; opacity: 0.9; }
        .content { padding: 30px; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 5px; }
        .article { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .article-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .article-summary { color: #666; margin-bottom: 15px; }
        .read-more { color: #667eea; text-decoration: none; font-weight: bold; }
        .cta-section { background: #667eea; color: white; padding: 30px; text-align: center; margin: 30px -30px -30px -30px; }
        .cta-title { font-size: 24px; font-weight: bold; margin-bottom: 15px; }
        .cta-button { display: inline-block; background: white; color: #667eea; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 15px; }
        .footer { background: #2c3e50; color: white; padding: 20px 30px; text-align: center; font-size: 14px; }
        .social-links { margin: 15px 0; }
        .social-links a { color: white; margin: 0 10px; text-decoration: none; }
        .divider { height: 2px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 30px 0; }
    </style>
</head>
<body>
    <div class="newsletter">
        <div class="header">
            <div class="logo">{{company_logo}}</div>
            <div class="newsletter-title">{{newsletter_title}}</div>
            <div class="newsletter-subtitle">{{newsletter_subtitle}}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">{{featured_section_title}}</div>
                {{featured_content}}
            </div>
            
            <div class="divider"></div>
            
            <div class="section">
                <div class="section-title">{{news_section_title}}</div>
                {{news_articles}}
            </div>
            
            <div class="section">
                <div class="section-title">{{tips_section_title}}</div>
                {{tips_content}}
            </div>
        </div>
        
        <div class="cta-section">
            <div class="cta-title">{{cta_title}}</div>
            <p>{{cta_description}}</p>
            <a href="{{cta_link}}" class="cta-button">{{cta_button_text}}</a>
        </div>
        
        <div class="footer">
            <div>{{company_name}} | {{company_address}}</div>
            <div class="social-links">
                {{social_links}}
            </div>
            <div>{{unsubscribe_text}}</div>
        </div>
    </div>
</body>
</html>
        """,
        placeholders=[
            ContentPlaceholder(key="company_logo", label="Company Logo", description="Company name or logo text", placeholder_text="TechCorp"),
            ContentPlaceholder(key="newsletter_title", label="Newsletter Title", description="Title of the newsletter", placeholder_text="Weekly Tech Insights"),
            ContentPlaceholder(key="newsletter_subtitle", label="Newsletter Subtitle", description="Subtitle or description", placeholder_text="Your weekly dose of technology news and insights"),
            ContentPlaceholder(key="featured_section_title", label="Featured Section Title", description="Title of the main featured section", placeholder_text="This Week's Spotlight"),
            ContentPlaceholder(key="featured_content", label="Featured Content", description="Main featured article or content", placeholder_text="<div class='article'><div class='article-title'>AI Revolution in 2024</div><div class='article-summary'>Artificial Intelligence continues to transform industries worldwide...</div><a href='#' class='read-more'>Read More →</a></div>", content_type="html"),
            ContentPlaceholder(key="news_section_title", label="News Section Title", description="Title for news section", placeholder_text="Industry News"),
            ContentPlaceholder(key="news_articles", label="News Articles", description="Collection of news articles", placeholder_text="<div class='article'><div class='article-title'>New Framework Released</div><div class='article-summary'>A groundbreaking new framework promises to simplify development...</div></div>", content_type="html"),
            ContentPlaceholder(key="tips_section_title", label="Tips Section Title", description="Title for tips section", placeholder_text="Pro Tips"),
            ContentPlaceholder(key="tips_content", label="Tips Content", description="Tips and advice content", placeholder_text="<ul><li>Optimize your workflow with these productivity hacks</li><li>Best practices for code organization</li><li>Security tips for modern applications</li></ul>", content_type="html"),
            ContentPlaceholder(key="cta_title", label="CTA Title", description="Call-to-action title", placeholder_text="Ready to Level Up?"),
            ContentPlaceholder(key="cta_description", label="CTA Description", description="Call-to-action description", placeholder_text="Join our premium community for exclusive content and early access to new features."),
            ContentPlaceholder(key="cta_link", label="CTA Link", description="Call-to-action link URL", placeholder_text="#"),
            ContentPlaceholder(key="cta_button_text", label="CTA Button Text", description="Text for the CTA button", placeholder_text="Join Now"),
            ContentPlaceholder(key="company_name", label="Company Name", description="Your company name", placeholder_text="TechCorp Solutions"),
            ContentPlaceholder(key="company_address", label="Company Address", description="Company address", placeholder_text="123 Tech Street, Innovation City, TC 12345"),
            ContentPlaceholder(key="social_links", label="Social Links", description="Social media links", placeholder_text="<a href='#'>Twitter</a> | <a href='#'>LinkedIn</a> | <a href='#'>Website</a>", content_type="html"),
            ContentPlaceholder(key="unsubscribe_text", label="Unsubscribe Text", description="Unsubscribe information", placeholder_text="You're receiving this because you subscribed to our newsletter. <a href='#' style='color: #bdc3c7;'>Unsubscribe</a>")
        ]
    )
    template_service.template_library.add_template(template)


def add_technical_templates(template_service):
    """Add technical templates to the template service."""
    
    # API Documentation Template
    template = Template(
        id="api_documentation",
        metadata=TemplateMetadata(
            name="API Documentation",
            description="Comprehensive API documentation with endpoints and examples",
            category=TemplateCategory.TECHNICAL,
            tags=["api", "documentation", "endpoints", "technical"],
            difficulty_level="intermediate",
            estimated_time="40 minutes"
        ),
        html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{api_name}} - API Documentation</title>
    <style>
        body { font-family: 'Monaco', 'Menlo', monospace; line-height: 1.6; margin: 0; background: #1e1e1e; color: #d4d4d4; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #0d1117; color: #58a6ff; padding: 40px; border-radius: 8px; margin-bottom: 30px; }
        .api-title { font-size: 36px; font-weight: bold; margin-bottom: 10px; }
        .api-version { font-size: 18px; opacity: 0.8; }
        .section { background: #161b22; padding: 30px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #30363d; }
        .section-title { font-size: 24px; font-weight: bold; color: #58a6ff; margin-bottom: 20px; border-bottom: 2px solid #21262d; padding-bottom: 10px; }
        .endpoint { background: #0d1117; padding: 20px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #238636; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 10px; }
        .method-get { background: #238636; color: white; }
        .method-post { background: #1f6feb; color: white; }
        .method-put { background: #fb8500; color: white; }
        .method-delete { background: #da3633; color: white; }
        .endpoint-url { font-size: 18px; font-weight: bold; color: #f0f6fc; }
        .endpoint-description { margin: 15px 0; color: #8b949e; }
        .code-block { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin: 15px 0; overflow-x: auto; }
        .code-block pre { margin: 0; color: #e6edf3; }
        .param-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .param-table th, .param-table td { border: 1px solid #30363d; padding: 12px; text-align: left; }
        .param-table th { background: #21262d; color: #f0f6fc; font-weight: bold; }
        .param-table td { background: #0d1117; }
        .required { color: #f85149; font-weight: bold; }
        .optional { color: #7d8590; }
        .response-code { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 8px; }
        .code-200 { background: #238636; color: white; }
        .code-400 { background: #fb8500; color: white; }
        .code-401 { background: #da3633; color: white; }
        .code-404 { background: #6f42c1; color: white; }
        .auth-note { background: #fff3cd; color: #856404; padding: 15px; border-radius: 6px; margin: 20px 0; border: 1px solid #ffeaa7; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="api-title">{{api_name}}</div>
            <div class="api-version">Version {{api_version}} | {{base_url}}</div>
            <p>{{api_description}}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Authentication</div>
            <div class="auth-note">{{auth_description}}</div>
            <div class="code-block">
                <pre>{{auth_example}}</pre>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Endpoints</div>
            {{endpoints}}
        </div>
        
        <div class="section">
            <div class="section-title">Error Handling</div>
            <p>{{error_description}}</p>
            <table class="param-table">
                <tr>
                    <th>Status Code</th>
                    <th>Description</th>
                    <th>Example Response</th>
                </tr>
                {{error_codes}}
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Rate Limiting</div>
            <p>{{rate_limit_description}}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Examples</div>
            {{usage_examples}}
        </div>
    </div>
</body>
</html>
        """,
        placeholders=[
            ContentPlaceholder(key="api_name", label="API Name", description="Name of the API", placeholder_text="TechCorp API"),
            ContentPlaceholder(key="api_version", label="API Version", description="Current API version", placeholder_text="v2.1"),
            ContentPlaceholder(key="base_url", label="Base URL", description="Base URL for the API", placeholder_text="https://api.techcorp.com/v2"),
            ContentPlaceholder(key="api_description", label="API Description", description="Brief description of the API", placeholder_text="A comprehensive REST API for managing user accounts, data processing, and analytics."),
            ContentPlaceholder(key="auth_description", label="Authentication Description", description="How authentication works", placeholder_text="All API requests require authentication using an API key in the Authorization header."),
            ContentPlaceholder(key="auth_example", label="Authentication Example", description="Example of authentication", placeholder_text="Authorization: Bearer YOUR_API_KEY"),
            ContentPlaceholder(key="endpoints", label="API Endpoints", description="List of API endpoints with details", placeholder_text="<div class='endpoint'><span class='method method-get'>GET</span><span class='endpoint-url'>/users</span><div class='endpoint-description'>Retrieve a list of users</div></div>", content_type="html"),
            ContentPlaceholder(key="error_description", label="Error Handling Description", description="Description of error handling", placeholder_text="The API uses standard HTTP status codes to indicate success or failure of requests."),
            ContentPlaceholder(key="error_codes", label="Error Codes", description="Table of error codes and descriptions", placeholder_text="<tr><td><span class='response-code code-400'>400</span></td><td>Bad Request</td><td>Invalid request parameters</td></tr>", content_type="html"),
            ContentPlaceholder(key="rate_limit_description", label="Rate Limiting", description="Rate limiting information", placeholder_text="API requests are limited to 1000 per hour per API key. Rate limit headers are included in all responses."),
            ContentPlaceholder(key="usage_examples", label="Usage Examples", description="Code examples and use cases", placeholder_text="<div class='code-block'><pre>curl -X GET 'https://api.techcorp.com/v2/users' \\\n  -H 'Authorization: Bearer YOUR_API_KEY'</pre></div>", content_type="html")
        ]
    )
    template_service.template_library.add_template(template)


def add_marketing_templates(template_service):
    """Add marketing templates to the template service."""
    
    # Press Release Template
    template = Template(
        id="press_release",
        metadata=TemplateMetadata(
            name="Press Release",
            description="Professional press release for announcements and news",
            category=TemplateCategory.MARKETING,
            tags=["press", "release", "announcement", "media", "news"],
            difficulty_level="intermediate",
            estimated_time="20 minutes"
        ),
        html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{headline}} - Press Release</title>
    <style>
        body { font-family: 'Times New Roman', serif; line-height: 1.6; margin: 40px auto; max-width: 800px; color: #333; }
        .letterhead { text-align: center; border-bottom: 3px solid #1e3a8a; padding-bottom: 20px; margin-bottom: 30px; }
        .company-name { font-size: 24px; font-weight: bold; color: #1e3a8a; margin-bottom: 5px; }
        .company-tagline { font-size: 14px; color: #666; font-style: italic; }
        .press-release-header { text-align: center; font-size: 20px; font-weight: bold; color: #1e3a8a; margin: 40px 0 20px 0; }
        .release-info { text-align: center; margin-bottom: 40px; }
        .release-date { font-weight: bold; margin-bottom: 10px; }
        .location { color: #666; }
        .headline { font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 20px; color: #1e3a8a; line-height: 1.3; }
        .subheadline { font-size: 18px; text-align: center; margin-bottom: 30px; color: #666; font-style: italic; }
        .body-text { font-size: 16px; margin-bottom: 20px; text-align: justify; }
        .quote { background: #f0f7ff; border-left: 4px solid #1e3a8a; padding: 20px; margin: 30px 0; font-style: italic; }
        .quote-attribution { text-align: right; margin-top: 15px; font-weight: bold; color: #1e3a8a; }
        .about-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 30px 0; }
        .about-title { font-weight: bold; color: #1e3a8a; margin-bottom: 10px; }
        .contact-info { border-top: 2px solid #e5e7eb; padding-top: 20px; margin-top: 40px; }
        .contact-title { font-weight: bold; color: #1e3a8a; margin-bottom: 15px; }
        .contact-details { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .footer { text-align: center; margin-top: 40px; font-size: 14px; color: #666; border-top: 1px solid #e5e7eb; padding-top: 20px; }
        .end-mark { text-align: center; font-size: 18px; font-weight: bold; margin: 30px 0; }
    </style>
</head>
<body>
    <div class="letterhead">
        <div class="company-name">{{company_name}}</div>
        <div class="company-tagline">{{company_tagline}}</div>
    </div>
    
    <div class="press-release-header">PRESS RELEASE</div>
    
    <div class="release-info">
        <div class="release-date">FOR IMMEDIATE RELEASE</div>
        <div class="location">{{release_date}} – {{location}}</div>
    </div>
    
    <h1 class="headline">{{headline}}</h1>
    <div class="subheadline">{{subheadline}}</div>
    
    <div class="body-text">{{opening_paragraph}}</div>
    
    <div class="body-text">{{body_content}}</div>
    
    <div class="quote">
        "{{quote_text}}"
        <div class="quote-attribution">– {{quote_attribution}}</div>
    </div>
    
    <div class="body-text">{{additional_content}}</div>
    
    <div class="about-section">
        <div class="about-title">About {{company_name}}</div>
        {{about_company}}
    </div>
    
    <div class="contact-info">
        <div class="contact-title">Media Contact</div>
        <div class="contact-details">
            <div>
                <strong>{{contact_name}}</strong><br>
                {{contact_title}}<br>
                Phone: {{contact_phone}}<br>
                Email: {{contact_email}}
            </div>
            <div>
                <strong>Company Information</strong><br>
                {{company_address}}<br>
                Website: {{company_website}}<br>
                {{additional_contact_info}}
            </div>
        </div>
    </div>
    
    <div class="end-mark">###</div>
    
    <div class="footer">
        <p>This press release may contain forward-looking statements. Please see our website for important disclaimers and additional information.</p>
    </div>
</body>
</html>
        """,
        placeholders=[
            ContentPlaceholder(key="company_name", label="Company Name", description="Name of the company", placeholder_text="TechCorp Solutions"),
            ContentPlaceholder(key="company_tagline", label="Company Tagline", description="Company tagline or motto", placeholder_text="Innovating the Future of Technology"),
            ContentPlaceholder(key="release_date", label="Release Date", description="Date of the press release", placeholder_text="December 9, 2024"),
            ContentPlaceholder(key="location", label="Location", description="City where the news originates", placeholder_text="San Francisco, CA"),
            ContentPlaceholder(key="headline", label="Headline", description="Main headline of the press release", placeholder_text="TechCorp Solutions Launches Revolutionary AI Platform, Transforming Industry Standards"),
            ContentPlaceholder(key="subheadline", label="Subheadline", description="Supporting headline", placeholder_text="New platform delivers 300% improvement in processing efficiency and sets new benchmarks for innovation"),
            ContentPlaceholder(key="opening_paragraph", label="Opening Paragraph", description="First paragraph with key information", placeholder_text="TechCorp Solutions, a leading technology innovator, today announced the launch of its groundbreaking AI platform that promises to revolutionize data processing across multiple industries. The new platform delivers unprecedented performance improvements while maintaining the highest standards of security and reliability."),
            ContentPlaceholder(key="body_content", label="Body Content", description="Main body content with details", placeholder_text="The innovative platform incorporates advanced machine learning algorithms and cutting-edge infrastructure to provide businesses with tools that were previously unavailable in the market. Early beta testing has shown remarkable results, with participating companies reporting significant improvements in operational efficiency and cost reduction."),
            ContentPlaceholder(key="quote_text", label="Quote Text", description="Key quote from spokesperson", placeholder_text="This launch represents a major milestone in our mission to democratize advanced AI technology. We're not just releasing a product; we're providing businesses with the tools they need to thrive in the digital age."),
            ContentPlaceholder(key="quote_attribution", label="Quote Attribution", description="Person who gave the quote", placeholder_text="Sarah Johnson, CEO of TechCorp Solutions"),
            ContentPlaceholder(key="additional_content", label="Additional Content", description="Additional details and information", placeholder_text="The platform will be available starting January 2025, with early access programs beginning next month. TechCorp Solutions plans to expand the platform's capabilities throughout 2025, with additional features and integrations planned for release in quarterly updates."),
            ContentPlaceholder(key="about_company", label="About Company", description="Company background information", placeholder_text="Founded in 2015, TechCorp Solutions is a leading provider of enterprise technology solutions, serving over 500 companies worldwide. The company specializes in AI-driven platforms and has been recognized for its innovation and commitment to customer success."),
            ContentPlaceholder(key="contact_name", label="Contact Name", description="Media contact person", placeholder_text="Michael Chen"),
            ContentPlaceholder(key="contact_title", label="Contact Title", description="Contact person's title", placeholder_text="Director of Communications"),
            ContentPlaceholder(key="contact_phone", label="Contact Phone", description="Contact phone number", placeholder_text="(555) 123-4567"),
            ContentPlaceholder(key="contact_email", label="Contact Email", description="Contact email address", placeholder_text="press@techcorp.com"),
            ContentPlaceholder(key="company_address", label="Company Address", description="Company address", placeholder_text="100 Innovation Drive, San Francisco, CA 94105"),
            ContentPlaceholder(key="company_website", label="Company Website", description="Company website URL", placeholder_text="www.techcorp.com"),
            ContentPlaceholder(key="additional_contact_info", label="Additional Contact Info", description="Additional contact information", placeholder_text="Investor Relations: investors@techcorp.com")
        ]
    )
    template_service.template_library.add_template(template)