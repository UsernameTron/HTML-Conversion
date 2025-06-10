"""Template service for managing document templates."""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from models.template_models import Template, TemplateLibrary, TemplateMetadata, ContentPlaceholder, TemplateCategory, StyleOverride
from utils.logger import get_enhanced_logger
from utils.cache_manager import get_cache_manager
from .template_library_extended import add_creative_templates, add_technical_templates, add_marketing_templates

logger = get_enhanced_logger(__name__)


class TemplateService:
    """Service for managing document templates."""
    
    def __init__(self):
        """Initialize template service."""
        self.cache_manager = get_cache_manager()
        self.template_library = TemplateLibrary()
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize the template library with default templates."""
        try:
            # Business Templates
            self._add_business_letter_template()
            self._add_business_proposal_template()
            self._add_meeting_minutes_template()
            self._add_project_status_template()
            
            # Academic Templates
            self._add_research_paper_template()
            
            # Add extended templates from separate module
            add_creative_templates(self)
            add_technical_templates(self)  
            add_marketing_templates(self)
            
            logger.info(f"Initialized template library with {len(self.template_library.templates)} templates")
            
        except Exception as e:
            logger.error(f"Error initializing default templates: {str(e)}")
    
    def get_template_library(self) -> TemplateLibrary:
        """Get the complete template library."""
        return self.template_library
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID."""
        return self.template_library.get_template(template_id)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[Template]:
        """Get all templates in a specific category."""
        return self.template_library.get_templates_by_category(category)
    
    def search_templates(self, query: str) -> List[Template]:
        """Search templates by name, description, or tags."""
        return self.template_library.search_templates(query)
    
    def render_template(self, template_id: str, content_data: Dict[str, str]) -> Optional[str]:
        """Render a template with provided content."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Validate content
        validation_errors = template.validate_content(content_data)
        if validation_errors:
            logger.warning(f"Template validation errors: {validation_errors}")
            return None
        
        return template.render(content_data)
    
    # Business Templates
    def _add_business_letter_template(self):
        """Add professional business letter template."""
        template = Template(
            id="business_letter",
            metadata=TemplateMetadata(
                name="Professional Business Letter",
                description="Formal business letter with company letterhead and professional formatting",
                category=TemplateCategory.BUSINESS,
                tags=["letter", "formal", "business", "correspondence"],
                difficulty_level="beginner",
                estimated_time="10 minutes"
            ),
            html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{document_title}}</title>
    <style>
        body { font-family: 'Times New Roman', serif; line-height: 1.6; margin: 40px; color: #333; }
        .letterhead { text-align: center; border-bottom: 2px solid #2c5aa0; padding-bottom: 20px; margin-bottom: 30px; }
        .company-name { font-size: 24px; font-weight: bold; color: #2c5aa0; margin-bottom: 5px; }
        .company-details { font-size: 12px; color: #666; }
        .date { text-align: right; margin-bottom: 30px; }
        .recipient { margin-bottom: 30px; }
        .subject { font-weight: bold; margin-bottom: 20px; }
        .content { margin-bottom: 30px; }
        .closing { margin-top: 40px; }
        .signature-space { margin-top: 60px; }
    </style>
</head>
<body>
    <div class="letterhead">
        <div class="company-name">{{company_name}}</div>
        <div class="company-details">{{company_address}} | {{company_phone}} | {{company_email}}</div>
    </div>
    
    <div class="date">{{date}}</div>
    
    <div class="recipient">
        {{recipient_name}}<br>
        {{recipient_title}}<br>
        {{recipient_company}}<br>
        {{recipient_address}}
    </div>
    
    <div class="subject">Subject: {{subject}}</div>
    
    <div class="content">
        <p>Dear {{recipient_salutation}},</p>
        {{letter_content}}
    </div>
    
    <div class="closing">
        <p>{{closing_phrase}},</p>
        <div class="signature-space">
            {{sender_name}}<br>
            {{sender_title}}<br>
            {{sender_company}}
        </div>
    </div>
</body>
</html>
            """,
            placeholders=[
                ContentPlaceholder(key="document_title", label="Document Title", description="Title for the document", placeholder_text="Business Letter"),
                ContentPlaceholder(key="company_name", label="Company Name", description="Your company name", placeholder_text="ABC Corporation"),
                ContentPlaceholder(key="company_address", label="Company Address", description="Company address", placeholder_text="123 Business St, City, State 12345"),
                ContentPlaceholder(key="company_phone", label="Company Phone", description="Company phone number", placeholder_text="(555) 123-4567"),
                ContentPlaceholder(key="company_email", label="Company Email", description="Company email address", placeholder_text="contact@company.com"),
                ContentPlaceholder(key="date", label="Date", description="Letter date", placeholder_text="December 9, 2024"),
                ContentPlaceholder(key="recipient_name", label="Recipient Name", description="Name of the recipient", placeholder_text="John Smith"),
                ContentPlaceholder(key="recipient_title", label="Recipient Title", description="Recipient's job title", placeholder_text="Senior Manager"),
                ContentPlaceholder(key="recipient_company", label="Recipient Company", description="Recipient's company", placeholder_text="XYZ Industries"),
                ContentPlaceholder(key="recipient_address", label="Recipient Address", description="Recipient's address", placeholder_text="456 Corporate Ave, City, State 67890"),
                ContentPlaceholder(key="subject", label="Subject", description="Letter subject", placeholder_text="Partnership Proposal"),
                ContentPlaceholder(key="recipient_salutation", label="Salutation", description="How to address recipient", placeholder_text="Mr. Smith"),
                ContentPlaceholder(key="letter_content", label="Letter Content", description="Main body of the letter", placeholder_text="<p>I hope this letter finds you well. I am writing to propose a strategic partnership between our organizations...</p>", content_type="html"),
                ContentPlaceholder(key="closing_phrase", label="Closing Phrase", description="Letter closing", placeholder_text="Sincerely"),
                ContentPlaceholder(key="sender_name", label="Sender Name", description="Your name", placeholder_text="Jane Doe"),
                ContentPlaceholder(key="sender_title", label="Sender Title", description="Your job title", placeholder_text="Business Development Manager"),
                ContentPlaceholder(key="sender_company", label="Sender Company", description="Your company name", placeholder_text="ABC Corporation")
            ],
            sample_content={
                "document_title": "Partnership Proposal Letter",
                "company_name": "TechCorp Solutions",
                "company_address": "100 Innovation Drive, Tech City, CA 94000",
                "company_phone": "(555) 987-6543",
                "company_email": "partnerships@techcorp.com",
                "date": "December 9, 2024",
                "recipient_name": "Sarah Johnson",
                "recipient_title": "Director of Partnerships",
                "recipient_company": "Global Industries Inc.",
                "recipient_address": "500 Corporate Plaza, Business City, NY 10001",
                "subject": "Strategic Partnership Opportunity",
                "recipient_salutation": "Ms. Johnson",
                "letter_content": "<p>I hope this letter finds you well. I am writing to propose a strategic partnership between TechCorp Solutions and Global Industries Inc. that I believe will be mutually beneficial to both organizations.</p><p>Our companies share similar values and complementary strengths that could create significant value for our customers. I would welcome the opportunity to discuss this proposal in detail at your convenience.</p><p>Please let me know if you would be available for a brief meeting in the coming weeks to explore this opportunity further.</p>",
                "closing_phrase": "Best regards",
                "sender_name": "Michael Chen",
                "sender_title": "Director of Business Development",
                "sender_company": "TechCorp Solutions"
            }
        )
        self.template_library.add_template(template)
    
    def _add_business_proposal_template(self):
        """Add business proposal template."""
        template = Template(
            id="business_proposal",
            metadata=TemplateMetadata(
                name="Business Proposal",
                description="Comprehensive business proposal with executive summary and detailed sections",
                category=TemplateCategory.BUSINESS,
                tags=["proposal", "business", "executive", "presentation"],
                difficulty_level="intermediate",
                estimated_time="30 minutes"
            ),
            html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{proposal_title}}</title>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; margin: 40px; color: #333; }
        .header { text-align: center; border-bottom: 3px solid #1e88e5; padding-bottom: 30px; margin-bottom: 40px; }
        .proposal-title { font-size: 32px; font-weight: bold; color: #1e88e5; margin-bottom: 10px; }
        .proposal-subtitle { font-size: 18px; color: #666; margin-bottom: 20px; }
        .company-info { font-size: 14px; color: #888; }
        .section { margin-bottom: 40px; }
        .section-title { font-size: 24px; font-weight: bold; color: #1e88e5; border-bottom: 2px solid #e3f2fd; padding-bottom: 10px; margin-bottom: 20px; }
        .subsection { margin-bottom: 25px; }
        .subsection-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; }
        .highlight-box { background: #e3f2fd; padding: 20px; border-left: 5px solid #1e88e5; margin: 20px 0; }
        .timeline-item { margin-bottom: 15px; padding-left: 20px; border-left: 3px solid #1e88e5; }
        .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <div class="proposal-title">{{proposal_title}}</div>
        <div class="proposal-subtitle">{{proposal_subtitle}}</div>
        <div class="company-info">
            Prepared by {{company_name}}<br>
            {{date}}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Executive Summary</div>
        {{executive_summary}}
    </div>
    
    <div class="section">
        <div class="section-title">Problem Statement</div>
        {{problem_statement}}
    </div>
    
    <div class="section">
        <div class="section-title">Proposed Solution</div>
        {{proposed_solution}}
        
        <div class="highlight-box">
            <strong>Key Benefits:</strong>
            {{key_benefits}}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Implementation Timeline</div>
        {{implementation_timeline}}
    </div>
    
    <div class="section">
        <div class="section-title">Investment & ROI</div>
        <div class="subsection">
            <div class="subsection-title">Investment Required</div>
            {{investment_details}}
        </div>
        <div class="subsection">
            <div class="subsection-title">Expected ROI</div>
            {{roi_details}}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Next Steps</div>
        {{next_steps}}
    </div>
    
    <div class="footer">
        {{company_name}} | {{contact_email}} | {{contact_phone}}
    </div>
</body>
</html>
            """,
            placeholders=[
                ContentPlaceholder(key="proposal_title", label="Proposal Title", description="Main title of the proposal", placeholder_text="Digital Transformation Initiative"),
                ContentPlaceholder(key="proposal_subtitle", label="Proposal Subtitle", description="Subtitle or tagline", placeholder_text="Modernizing Operations for the Digital Age"),
                ContentPlaceholder(key="company_name", label="Company Name", description="Your company name", placeholder_text="Innovation Partners LLC"),
                ContentPlaceholder(key="date", label="Date", description="Proposal date", placeholder_text="December 9, 2024"),
                ContentPlaceholder(key="executive_summary", label="Executive Summary", description="Brief overview of the proposal", placeholder_text="<p>This proposal outlines a comprehensive digital transformation strategy...</p>", content_type="html"),
                ContentPlaceholder(key="problem_statement", label="Problem Statement", description="Description of the problem being addressed", placeholder_text="<p>Current systems are outdated and inefficient...</p>", content_type="html"),
                ContentPlaceholder(key="proposed_solution", label="Proposed Solution", description="Detailed solution description", placeholder_text="<p>We propose implementing a modern, cloud-based solution...</p>", content_type="html"),
                ContentPlaceholder(key="key_benefits", label="Key Benefits", description="List of main benefits", placeholder_text="<ul><li>50% reduction in processing time</li><li>Enhanced security</li><li>Improved scalability</li></ul>", content_type="html"),
                ContentPlaceholder(key="implementation_timeline", label="Implementation Timeline", description="Project timeline and milestones", placeholder_text="<div class='timeline-item'><strong>Phase 1 (Months 1-2):</strong> Analysis and Planning</div>", content_type="html"),
                ContentPlaceholder(key="investment_details", label="Investment Details", description="Cost breakdown and investment required", placeholder_text="<p>Total investment: $150,000 over 6 months...</p>", content_type="html"),
                ContentPlaceholder(key="roi_details", label="ROI Details", description="Return on investment projections", placeholder_text="<p>Expected ROI of 250% within 18 months...</p>", content_type="html"),
                ContentPlaceholder(key="next_steps", label="Next Steps", description="Proposed next steps", placeholder_text="<ol><li>Review and approve proposal</li><li>Sign engagement letter</li><li>Begin discovery phase</li></ol>", content_type="html"),
                ContentPlaceholder(key="contact_email", label="Contact Email", description="Contact email address", placeholder_text="contact@company.com"),
                ContentPlaceholder(key="contact_phone", label="Contact Phone", description="Contact phone number", placeholder_text="(555) 123-4567")
            ]
        )
        self.template_library.add_template(template)
    
    def _add_meeting_minutes_template(self):
        """Add meeting minutes template."""
        template = Template(
            id="meeting_minutes",
            metadata=TemplateMetadata(
                name="Meeting Minutes",
                description="Professional meeting minutes with action items and decisions",
                category=TemplateCategory.BUSINESS,
                tags=["meeting", "minutes", "notes", "action-items"],
                difficulty_level="beginner",
                estimated_time="15 minutes"
            ),
            html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{meeting_title}} - Minutes</title>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; margin: 40px; color: #333; }
        .header { border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }
        .meeting-title { font-size: 28px; font-weight: bold; color: #4CAF50; margin-bottom: 10px; }
        .meeting-info { background: #f1f8e9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .info-item { margin-bottom: 10px; }
        .label { font-weight: bold; color: #388e3c; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 20px; font-weight: bold; color: #4CAF50; border-bottom: 1px solid #c8e6c9; padding-bottom: 8px; margin-bottom: 15px; }
        .attendee-list { columns: 2; column-gap: 30px; }
        .action-item { background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .action-header { font-weight: bold; color: #e65100; margin-bottom: 8px; }
        .decision-item { background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .priority-high { border-left-color: #f44336; }
        .priority-medium { border-left-color: #ff9800; }
        .priority-low { border-left-color: #4CAF50; }
    </style>
</head>
<body>
    <div class="header">
        <div class="meeting-title">{{meeting_title}}</div>
        <div class="meeting-info">
            <div class="info-grid">
                <div class="info-item"><span class="label">Date:</span> {{meeting_date}}</div>
                <div class="info-item"><span class="label">Time:</span> {{meeting_time}}</div>
                <div class="info-item"><span class="label">Location:</span> {{meeting_location}}</div>
                <div class="info-item"><span class="label">Chair:</span> {{meeting_chair}}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Attendees</div>
        <div class="attendee-list">
            {{attendees}}
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Agenda Items & Discussion</div>
        {{agenda_discussion}}
    </div>
    
    <div class="section">
        <div class="section-title">Decisions Made</div>
        {{decisions}}
    </div>
    
    <div class="section">
        <div class="section-title">Action Items</div>
        {{action_items}}
    </div>
    
    <div class="section">
        <div class="section-title">Next Meeting</div>
        {{next_meeting}}
    </div>
</body>
</html>
            """,
            placeholders=[
                ContentPlaceholder(key="meeting_title", label="Meeting Title", description="Title of the meeting", placeholder_text="Weekly Team Standup"),
                ContentPlaceholder(key="meeting_date", label="Meeting Date", description="Date of the meeting", placeholder_text="December 9, 2024"),
                ContentPlaceholder(key="meeting_time", label="Meeting Time", description="Time and duration", placeholder_text="2:00 PM - 3:00 PM PST"),
                ContentPlaceholder(key="meeting_location", label="Meeting Location", description="Location or platform", placeholder_text="Conference Room A / Zoom"),
                ContentPlaceholder(key="meeting_chair", label="Meeting Chair", description="Person who chaired the meeting", placeholder_text="Sarah Johnson"),
                ContentPlaceholder(key="attendees", label="Attendees", description="List of meeting attendees", placeholder_text="<ul><li>John Smith - Project Manager</li><li>Alice Brown - Developer</li><li>Bob Wilson - Designer</li></ul>", content_type="html"),
                ContentPlaceholder(key="agenda_discussion", label="Agenda & Discussion", description="Discussion points and agenda items", placeholder_text="<p><strong>1. Project Status Update</strong><br>Current milestone completion at 85%...</p>", content_type="html"),
                ContentPlaceholder(key="decisions", label="Decisions Made", description="Key decisions from the meeting", placeholder_text="<div class='decision-item'>Decision to extend deadline by one week due to scope changes</div>", content_type="html"),
                ContentPlaceholder(key="action_items", label="Action Items", description="Action items with owners and due dates", placeholder_text="<div class='action-item'><div class='action-header'>High Priority</div>Complete user testing by Friday - Assigned to Alice</div>", content_type="html"),
                ContentPlaceholder(key="next_meeting", label="Next Meeting", description="Information about the next meeting", placeholder_text="<p><strong>Date:</strong> December 16, 2024<br><strong>Time:</strong> 2:00 PM PST<br><strong>Agenda:</strong> Final testing results review</p>", content_type="html")
            ]
        )
        self.template_library.add_template(template)
    
    def _add_project_status_template(self):
        """Add project status report template."""
        template = Template(
            id="project_status",
            metadata=TemplateMetadata(
                name="Project Status Report",
                description="Comprehensive project status report with metrics and timeline",
                category=TemplateCategory.BUSINESS,
                tags=["project", "status", "report", "progress", "management"],
                difficulty_level="intermediate",
                estimated_time="25 minutes"
            ),
            html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{project_name}} - Status Report</title>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; margin: 40px; color: #333; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
        .project-title { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
        .report-info { font-size: 14px; opacity: 0.9; }
        .status-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .status-card { background: white; border: 2px solid #e0e0e0; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status-value { font-size: 32px; font-weight: bold; margin-bottom: 8px; }
        .status-label { font-size: 14px; color: #666; }
        .green { color: #4CAF50; border-color: #4CAF50; }
        .orange { color: #ff9800; border-color: #ff9800; }
        .red { color: #f44336; border-color: #f44336; }
        .blue { color: #2196F3; border-color: #2196F3; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 22px; font-weight: bold; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }
        .progress-bar { background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%); transition: width 0.3s; }
        .milestone { background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .milestone-title { font-weight: bold; color: #333; margin-bottom: 8px; }
        .milestone-status { font-size: 12px; padding: 4px 8px; border-radius: 4px; color: white; display: inline-block; }
        .status-completed { background: #4CAF50; }
        .status-in-progress { background: #ff9800; }
        .status-pending { background: #9e9e9e; }
        .risk-item { background: #ffebee; border-left: 4px solid #f44336; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
        .risk-level { font-weight: bold; color: #c62828; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="project-title">{{project_name}}</div>
        <div class="report-info">Status Report | {{report_date}} | {{report_period}}</div>
    </div>
    
    <div class="status-overview">
        <div class="status-card green">
            <div class="status-value">{{completion_percentage}}%</div>
            <div class="status-label">Complete</div>
        </div>
        <div class="status-card blue">
            <div class="status-value">{{days_remaining}}</div>
            <div class="status-label">Days Remaining</div>
        </div>
        <div class="status-card orange">
            <div class="status-value">{{budget_used}}%</div>
            <div class="status-label">Budget Used</div>
        </div>
        <div class="status-card {{team_status_color}}">
            <div class="status-value">{{team_size}}</div>
            <div class="status-label">Team Members</div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Executive Summary</div>
        {{executive_summary}}
    </div>
    
    <div class="section">
        <div class="section-title">Progress Overview</div>
        {{progress_overview}}
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{completion_percentage}}%"></div>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">Key Milestones</div>
        {{milestones}}
    </div>
    
    <div class="section">
        <div class="section-title">Accomplishments This Period</div>
        {{accomplishments}}
    </div>
    
    <div class="section">
        <div class="section-title">Upcoming Activities</div>
        {{upcoming_activities}}
    </div>
    
    <div class="section">
        <div class="section-title">Risks & Issues</div>
        {{risks_issues}}
    </div>
    
    <div class="section">
        <div class="section-title">Budget Status</div>
        {{budget_status}}
    </div>
    
    <div class="section">
        <div class="section-title">Next Steps</div>
        {{next_steps}}
    </div>
</body>
</html>
            """,
            placeholders=[
                ContentPlaceholder(key="project_name", label="Project Name", description="Name of the project", placeholder_text="Website Redesign Project"),
                ContentPlaceholder(key="report_date", label="Report Date", description="Date of this status report", placeholder_text="December 9, 2024"),
                ContentPlaceholder(key="report_period", label="Report Period", description="Period covered by this report", placeholder_text="Week ending December 9, 2024"),
                ContentPlaceholder(key="completion_percentage", label="Completion Percentage", description="Project completion percentage", placeholder_text="75"),
                ContentPlaceholder(key="days_remaining", label="Days Remaining", description="Days remaining to completion", placeholder_text="15"),
                ContentPlaceholder(key="budget_used", label="Budget Used", description="Percentage of budget used", placeholder_text="68"),
                ContentPlaceholder(key="team_size", label="Team Size", description="Number of team members", placeholder_text="8"),
                ContentPlaceholder(key="team_status_color", label="Team Status Color", description="Color indicator for team status", placeholder_text="green"),
                ContentPlaceholder(key="executive_summary", label="Executive Summary", description="Brief project overview", placeholder_text="<p>Project is progressing well with 75% completion. On track to meet deadline...</p>", content_type="html"),
                ContentPlaceholder(key="progress_overview", label="Progress Overview", description="Detailed progress description", placeholder_text="<p>Completed design phase and development is 80% complete...</p>", content_type="html"),
                ContentPlaceholder(key="milestones", label="Key Milestones", description="Project milestones with status", placeholder_text="<div class='milestone'><div class='milestone-title'>Design Phase <span class='milestone-status status-completed'>Completed</span></div>Wireframes and mockups finalized</div>", content_type="html"),
                ContentPlaceholder(key="accomplishments", label="Accomplishments", description="Recent accomplishments", placeholder_text="<ul><li>Completed user interface design</li><li>Implemented responsive layout</li><li>Conducted user testing</li></ul>", content_type="html"),
                ContentPlaceholder(key="upcoming_activities", label="Upcoming Activities", description="Planned activities for next period", placeholder_text="<ul><li>Finalize backend integration</li><li>Complete quality assurance testing</li><li>Prepare for production deployment</li></ul>", content_type="html"),
                ContentPlaceholder(key="risks_issues", label="Risks & Issues", description="Current risks and issues", placeholder_text="<div class='risk-item'><div class='risk-level'>Medium Risk</div>Third-party API integration may cause delays</div>", content_type="html"),
                ContentPlaceholder(key="budget_status", label="Budget Status", description="Current budget situation", placeholder_text="<p>Project is within budget with $32,000 of $100,000 remaining...</p>", content_type="html"),
                ContentPlaceholder(key="next_steps", label="Next Steps", description="Immediate next steps", placeholder_text="<ol><li>Complete API integration testing</li><li>Schedule final review meeting</li><li>Prepare deployment plan</li></ol>", content_type="html")
            ]
        )
        self.template_library.add_template(template)
    
    # Academic Templates
    def _add_research_paper_template(self):
        """Add academic research paper template."""
        template = Template(
            id="research_paper",
            metadata=TemplateMetadata(
                name="Academic Research Paper",
                description="Formal academic research paper with proper citations and structure",
                category=TemplateCategory.ACADEMIC,
                tags=["research", "academic", "paper", "citations", "formal"],
                difficulty_level="advanced",
                estimated_time="45 minutes"
            ),
            html_template="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{paper_title}}</title>
    <style>
        body { font-family: 'Times New Roman', serif; line-height: 2.0; margin: 1in; color: #000; font-size: 12pt; }
        .header { text-align: center; margin-bottom: 2in; }
        .title { font-size: 14pt; font-weight: bold; margin-bottom: 1in; }
        .author-info { margin-bottom: 0.5in; }
        .author-name { font-weight: bold; }
        .affiliation { font-style: italic; }
        .abstract { margin: 2em 0; }
        .abstract-title { font-weight: bold; text-align: center; margin-bottom: 1em; }
        .keywords { margin: 1em 0; }
        .section-title { font-weight: bold; margin-top: 2em; margin-bottom: 1em; }
        .subsection-title { font-weight: bold; margin-top: 1.5em; margin-bottom: 0.5em; }
        .citation { font-size: 11pt; }
        .references { margin-top: 2em; }
        .reference-item { margin-bottom: 1em; text-indent: -0.5in; margin-left: 0.5in; }
        .page-break { page-break-before: always; }
        .figure { text-align: center; margin: 2em 0; }
        .figure-caption { font-size: 11pt; margin-top: 0.5em; }
        .table { margin: 2em auto; border-collapse: collapse; }
        .table th, .table td { border: 1px solid #000; padding: 8px; text-align: left; }
        .footnote { font-size: 10pt; margin-top: 2em; border-top: 1px solid #ccc; padding-top: 1em; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{{paper_title}}</div>
        <div class="author-info">
            <div class="author-name">{{author_name}}</div>
            <div class="affiliation">{{author_affiliation}}</div>
            <div>{{author_email}}</div>
        </div>
    </div>
    
    <div class="abstract">
        <div class="abstract-title">Abstract</div>
        {{abstract_content}}
        <div class="keywords"><strong>Keywords:</strong> {{keywords}}</div>
    </div>
    
    <div class="section-title">1. Introduction</div>
    {{introduction}}
    
    <div class="section-title">2. Literature Review</div>
    {{literature_review}}
    
    <div class="section-title">3. Methodology</div>
    {{methodology}}
    
    <div class="section-title">4. Results</div>
    {{results}}
    
    <div class="section-title">5. Discussion</div>
    {{discussion}}
    
    <div class="section-title">6. Conclusion</div>
    {{conclusion}}
    
    <div class="section-title">7. Future Work</div>
    {{future_work}}
    
    <div class="page-break"></div>
    <div class="references">
        <div class="section-title">References</div>
        {{references}}
    </div>
    
    <div class="footnote">
        {{footnotes}}
    </div>
</body>
</html>
            """,
            placeholders=[
                ContentPlaceholder(key="paper_title", label="Paper Title", description="Title of the research paper", placeholder_text="The Impact of Machine Learning on Modern Data Analysis"),
                ContentPlaceholder(key="author_name", label="Author Name", description="Name of the author(s)", placeholder_text="Dr. Jane Smith, Ph.D."),
                ContentPlaceholder(key="author_affiliation", label="Author Affiliation", description="University or institution", placeholder_text="Department of Computer Science, University of Technology"),
                ContentPlaceholder(key="author_email", label="Author Email", description="Contact email", placeholder_text="j.smith@university.edu"),
                ContentPlaceholder(key="abstract_content", label="Abstract", description="Research abstract (150-250 words)", placeholder_text="<p>This study examines the transformative impact of machine learning algorithms on contemporary data analysis methodologies...</p>", content_type="html"),
                ContentPlaceholder(key="keywords", label="Keywords", description="Research keywords (3-6 terms)", placeholder_text="machine learning, data analysis, algorithms, artificial intelligence, big data"),
                ContentPlaceholder(key="introduction", label="Introduction", description="Introduction section with background and objectives", placeholder_text="<p>The rapid advancement of machine learning technologies has fundamentally transformed...</p>", content_type="html"),
                ContentPlaceholder(key="literature_review", label="Literature Review", description="Review of relevant literature", placeholder_text="<p>Previous research in this field has established several key principles...</p>", content_type="html"),
                ContentPlaceholder(key="methodology", label="Methodology", description="Research methodology and approach", placeholder_text="<p>This study employed a mixed-methods approach combining quantitative analysis...</p>", content_type="html"),
                ContentPlaceholder(key="results", label="Results", description="Research findings and results", placeholder_text="<p>The analysis revealed significant improvements in processing efficiency...</p>", content_type="html"),
                ContentPlaceholder(key="discussion", label="Discussion", description="Discussion of results and implications", placeholder_text="<p>These findings suggest that machine learning approaches offer substantial advantages...</p>", content_type="html"),
                ContentPlaceholder(key="conclusion", label="Conclusion", description="Research conclusions", placeholder_text="<p>In conclusion, this research demonstrates the significant potential of machine learning...</p>", content_type="html"),
                ContentPlaceholder(key="future_work", label="Future Work", description="Suggestions for future research", placeholder_text="<p>Future research should investigate the scalability of these approaches...</p>", content_type="html"),
                ContentPlaceholder(key="references", label="References", description="Academic references in proper format", placeholder_text="<div class='reference-item'>Smith, J. (2023). Machine Learning Fundamentals. Journal of Computer Science, 45(2), 123-145.</div>", content_type="html"),
                ContentPlaceholder(key="footnotes", label="Footnotes", description="Additional footnotes if needed", placeholder_text="<p>¹ Additional methodological details available upon request.</p>", content_type="html", required=False)
            ]
        )
        self.template_library.add_template(template)