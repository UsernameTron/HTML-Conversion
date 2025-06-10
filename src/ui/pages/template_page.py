"""Template management page for creating and editing document templates."""

import streamlit as st
import json
from typing import Dict, List, Optional
from models.template_models import Template, TemplateCategory
from services.template_service import TemplateService
from utils.logger import get_enhanced_logger

logger = get_enhanced_logger(__name__)


class TemplatePage:
    """Template management interface."""
    
    def __init__(self):
        """Initialize template page."""
        self.template_service = TemplateService()
    
    def render(self):
        """Render the template management page."""
        st.header("📋 Document Templates")
        
        # Template navigation tabs
        tab1, tab2, tab3 = st.tabs(["📚 Browse Templates", "✨ Use Template", "🔧 Template Manager"])
        
        with tab1:
            self._render_template_browser()
        
        with tab2:
            self._render_template_editor()
        
        with tab3:
            self._render_template_manager()
    
    def _render_template_browser(self):
        """Render template browsing interface."""
        st.subheader("📚 Browse Document Templates")
        
        # Category filter
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.write("**Filter by Category:**")
            selected_categories = []
            for category in TemplateCategory:
                if st.checkbox(category.value.title(), key=f"cat_{category.value}"):
                    selected_categories.append(category)
            
            # Search
            search_query = st.text_input("🔍 Search templates", placeholder="Search by name, description, or tags...")
        
        with col2:
            # Get templates based on filters
            if selected_categories:
                templates = []
                for category in selected_categories:
                    templates.extend(self.template_service.get_templates_by_category(category))
            else:
                templates = list(self.template_service.template_library.templates.values())
            
            # Apply search filter
            if search_query:
                search_results = self.template_service.search_templates(search_query)
                if selected_categories:
                    # Intersection of category and search results
                    templates = [t for t in templates if t in search_results]
                else:
                    templates = search_results
            
            # Display templates
            if templates:
                for template in templates:
                    self._render_template_card(template)
            else:
                st.info("No templates found matching your criteria. Try adjusting your filters.")
        
        # Library statistics
        st.sidebar.subheader("📊 Template Library Stats")
        stats = self.template_service.template_library.get_template_stats()
        st.sidebar.metric("Total Templates", stats['total_templates'])
        
        st.sidebar.write("**By Category:**")
        for category, count in stats['categories'].items():
            st.sidebar.write(f"• {category.title()}: {count}")
    
    def _render_template_card(self, template: Template):
        """Render a template card."""
        with st.expander(f"📄 {template.metadata.name}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {template.metadata.description}")
                st.write(f"**Category:** {template.metadata.category.value.title()}")
                st.write(f"**Difficulty:** {template.metadata.difficulty_level.title()}")
                st.write(f"**Est. Time:** {template.metadata.estimated_time}")
                
                if template.metadata.tags:
                    tags_html = " ".join([f"<span style='background: #e3f2fd; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin: 2px;'>{tag}</span>" for tag in template.metadata.tags])
                    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
            
            with col2:
                if st.button("✨ Use Template", key=f"use_{template.id}"):
                    st.session_state.selected_template = template.id
                    st.success(f"Selected template: {template.metadata.name}")
                    st.rerun()
                
                if st.button("👁️ Preview", key=f"preview_{template.id}"):
                    self._show_template_preview(template)
                
                if st.button("📋 View Details", key=f"details_{template.id}"):
                    self._show_template_details(template)
    
    def _render_template_editor(self):
        """Render template content editor."""
        st.subheader("✨ Use Template")
        
        # Template selection
        if 'selected_template' not in st.session_state:
            st.info("👆 Please select a template from the Browse Templates tab first.")
            return
        
        template = self.template_service.get_template(st.session_state.selected_template)
        if not template:
            st.error("Selected template not found.")
            return
        
        st.success(f"📋 **Selected Template:** {template.metadata.name}")
        st.write(f"**Description:** {template.metadata.description}")
        
        # Content input form
        with st.form("template_content_form"):
            st.subheader("📝 Fill in Template Content")
            
            content_data = {}
            
            # Required placeholders first
            required_placeholders = template.get_required_placeholders()
            if required_placeholders:
                st.write("**Required Fields:**")
                for placeholder in required_placeholders:
                    content_data[placeholder.key] = self._render_placeholder_input(placeholder, required=True)
            
            # Optional placeholders
            optional_placeholders = [p for p in template.placeholders if not p.required]
            if optional_placeholders:
                with st.expander("⚙️ Optional Fields", expanded=False):
                    for placeholder in optional_placeholders:
                        content_data[placeholder.key] = self._render_placeholder_input(placeholder, required=False)
            
            # Generate button
            if st.form_submit_button("🎨 Generate Document", use_container_width=True):
                self._generate_template_document(template, content_data)
    
    def _render_placeholder_input(self, placeholder, required=True):
        """Render input field for a placeholder."""
        label = f"{placeholder.label}" + (" *" if required else "")
        help_text = placeholder.description
        
        if placeholder.content_type == "html":
            value = st.text_area(
                label,
                value=placeholder.placeholder_text if not required else "",
                help=help_text,
                height=100,
                key=f"input_{placeholder.key}"
            )
        else:
            value = st.text_input(
                label,
                value=placeholder.placeholder_text if not required else "",
                help=help_text,
                max_chars=placeholder.max_length,
                key=f"input_{placeholder.key}"
            )
        
        return value if value else placeholder.placeholder_text
    
    def _generate_template_document(self, template: Template, content_data: Dict[str, str]):
        """Generate document from template and content."""
        try:
            # Validate content
            validation_errors = template.validate_content(content_data)
            if validation_errors:
                st.error("❌ **Validation Errors:**")
                for error in validation_errors:
                    st.write(f"• {error}")
                return
            
            # Render template
            rendered_html = template.render(content_data)
            
            if rendered_html:
                st.success("✅ **Document Generated Successfully!**")
                
                # Store in session state for main app to use
                st.session_state.processed_content = rendered_html
                st.session_state.template_generated = True
                
                # Preview
                with st.expander("👁️ Document Preview", expanded=True):
                    st.markdown(rendered_html, unsafe_allow_html=True)
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📥 Download HTML",
                        data=rendered_html,
                        file_name=f"{template.metadata.name.lower().replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("📋 Copy to Main Editor", use_container_width=True):
                        st.success("Content copied to main editor! Go to the main page to continue editing.")
                
                with col3:
                    if st.button("🔄 Use in Main App", use_container_width=True):
                        st.switch_page("pages/main.py")
            else:
                st.error("❌ Failed to generate document from template.")
                
        except Exception as e:
            logger.error(f"Template generation error: {str(e)}")
            st.error(f"❌ **Generation Error:** {str(e)}")
    
    def _render_template_manager(self):
        """Render template management interface."""
        st.subheader("🔧 Template Manager")
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Library Statistics", use_container_width=True):
                self._show_library_statistics()
        
        with col2:
            if st.button("📤 Export Templates", use_container_width=True):
                self._export_templates()
        
        with col3:
            if st.button("📥 Import Templates", use_container_width=True):
                self._import_templates()
        
        st.divider()
        
        # Template list with management options
        st.write("**All Templates:**")
        
        templates = list(self.template_service.template_library.templates.values())
        
        for template in templates:
            with st.expander(f"🔧 {template.metadata.name}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.json({
                        "ID": template.id,
                        "Category": template.metadata.category.value,
                        "Placeholders": len(template.placeholders),
                        "Required Fields": len(template.get_required_placeholders()),
                        "Tags": template.metadata.tags,
                        "Created": template.metadata.created_date.strftime("%Y-%m-%d"),
                        "Modified": template.metadata.modified_date.strftime("%Y-%m-%d")
                    })
                
                with col2:
                    if st.button("📤 Export JSON", key=f"export_{template.id}"):
                        self._export_single_template(template)
                    
                    if st.button("📋 Clone", key=f"clone_{template.id}"):
                        st.info("Clone functionality would allow creating a copy of this template for editing.")
                    
                    if st.button("🗑️ Remove", key=f"remove_{template.id}"):
                        st.warning("Remove functionality would be available in a full implementation.")
    
    def _show_template_preview(self, template: Template):
        """Show template preview with sample content."""
        st.subheader(f"👁️ Preview: {template.metadata.name}")
        
        if template.sample_content:
            rendered_html = template.render(template.sample_content)
            st.markdown(rendered_html, unsafe_allow_html=True)
        else:
            st.info("No sample content available for this template.")
    
    def _show_template_details(self, template: Template):
        """Show detailed template information."""
        st.subheader(f"📋 Details: {template.metadata.name}")
        
        # Template metadata
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Template Information:**")
            st.json({
                "ID": template.id,
                "Name": template.metadata.name,
                "Description": template.metadata.description,
                "Category": template.metadata.category.value,
                "Difficulty": template.metadata.difficulty_level,
                "Estimated Time": template.metadata.estimated_time,
                "Author": template.metadata.author,
                "Version": template.metadata.version
            })
        
        with col2:
            st.write("**Placeholders:**")
            for placeholder in template.placeholders:
                st.write(f"• **{placeholder.label}** ({'Required' if placeholder.required else 'Optional'})")
                st.write(f"  _{placeholder.description}_")
        
        # Raw template HTML
        with st.expander("📄 Raw HTML Template", expanded=False):
            st.code(template.html_template, language='html')
    
    def _show_library_statistics(self):
        """Show detailed library statistics."""
        stats = self.template_service.template_library.get_template_stats()
        
        st.subheader("📊 Template Library Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Templates", stats['total_templates'])
        
        with col2:
            avg_placeholders = sum(len(t.placeholders) for t in self.template_service.template_library.templates.values()) / stats['total_templates']
            st.metric("Avg. Placeholders", f"{avg_placeholders:.1f}")
        
        with col3:
            total_required = sum(len(t.get_required_placeholders()) for t in self.template_service.template_library.templates.values())
            st.metric("Total Required Fields", total_required)
        
        # Category breakdown
        st.write("**Templates by Category:**")
        for category, count in stats['categories'].items():
            st.write(f"• **{category.title()}:** {count} templates")
        
        # Recent templates
        if stats['recent_templates']:
            st.write("**Recently Added:**")
            for template_id in stats['recent_templates']:
                template = self.template_service.get_template(template_id)
                if template:
                    st.write(f"• {template.metadata.name} ({template.metadata.category.value})")
    
    def _export_templates(self):
        """Export all templates as JSON."""
        templates_data = {}
        for template_id, template in self.template_service.template_library.templates.items():
            templates_data[template_id] = template.dict()
        
        json_data = json.dumps(templates_data, indent=2, default=str)
        
        st.download_button(
            "📥 Download All Templates (JSON)",
            data=json_data,
            file_name="template_library.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.success("✅ Template library ready for download!")
    
    def _export_single_template(self, template: Template):
        """Export a single template as JSON."""
        json_data = template.to_json()
        
        st.download_button(
            f"📥 Download {template.metadata.name}",
            data=json_data,
            file_name=f"{template.id}.json",
            mime="application/json",
            key=f"download_{template.id}"
        )
        
        st.success(f"✅ {template.metadata.name} ready for download!")
    
    def _import_templates(self):
        """Import templates from JSON file."""
        st.write("**Import Templates:**")
        
        uploaded_file = st.file_uploader(
            "Choose template JSON file",
            type=['json'],
            help="Upload a JSON file containing template definitions"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                data = json.loads(content)
                
                # Validate and preview the templates
                st.write("**Preview of templates to import:**")
                
                if isinstance(data, dict):
                    for template_id, template_data in data.items():
                        st.write(f"• {template_data.get('metadata', {}).get('name', template_id)}")
                
                if st.button("✅ Confirm Import"):
                    st.info("Import functionality would be implemented in a full version.")
                    st.success("Templates would be imported successfully!")
                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please check the file format.")
            except Exception as e:
                st.error(f"❌ Import error: {str(e)}")