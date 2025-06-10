"""Advanced PDF text extraction with multiple strategies."""

import logging
import base64
from io import BytesIO
from typing import Tuple, Optional, Dict, Any
import streamlit as st

# PDF processing libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Advanced PDF processor with multiple extraction strategies."""
    
    def __init__(self):
        """Initialize PDF processor with available libraries."""
        self.strategies = []
        
        if PDFPLUMBER_AVAILABLE:
            self.strategies.append(('pdfplumber', self._extract_with_pdfplumber))
        
        if PYPDF_AVAILABLE:
            self.strategies.append(('pypdf', self._extract_with_pypdf))
        
        if not self.strategies:
            logger.error("No PDF processing libraries available")
    
    def extract_text_from_pdf(self, file_obj, filename: str) -> Tuple[bool, str]:
        """
        Extract text from PDF using multiple strategies.
        
        Args:
            file_obj: File object containing PDF data
            filename: Name of the PDF file
            
        Returns:
            Tuple of (success, extracted_content_or_error)
        """
        if not self.strategies:
            return False, "No PDF processing libraries available. Please install PyPDF2 or pdfplumber."
        
        # Reset file pointer
        file_obj.seek(0)
        file_data = file_obj.read()
        file_size = len(file_data)
        
        # Validate file size (50MB limit)
        if file_size > 50 * 1024 * 1024:
            return False, "PDF file too large (max 50MB)"
        
        logger.info(f"Processing PDF: {filename} ({file_size:,} bytes)")
        
        # Try extraction strategies in order
        last_error = ""
        
        for strategy_name, strategy_func in self.strategies:
            try:
                logger.info(f"Trying PDF extraction with {strategy_name}")
                
                # Create new BytesIO for each attempt
                pdf_stream = BytesIO(file_data)
                
                success, result = strategy_func(pdf_stream, filename)
                
                if success and result.strip():
                    logger.info(f"Successfully extracted {len(result):,} characters using {strategy_name}")
                    return True, self._format_pdf_content(result, filename, file_size, strategy_name)
                else:
                    last_error = result if result else f"{strategy_name} extraction failed"
                    
            except Exception as e:
                last_error = f"{strategy_name} error: {str(e)}"
                logger.warning(f"PDF extraction failed with {strategy_name}: {str(e)}")
                continue
        
        # All strategies failed, return enhanced placeholder
        logger.warning(f"All PDF extraction strategies failed for {filename}")
        return True, self._create_enhanced_placeholder(filename, file_size, last_error)
    
    def _extract_with_pdfplumber(self, pdf_stream: BytesIO, filename: str) -> Tuple[bool, str]:
        """Extract text using pdfplumber (best for complex layouts)."""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_stream) as pdf:
                text_parts = []
                total_pages = len(pdf.pages)
                # Limit processing to first 50 pages for performance
                max_pages = min(total_pages, 50)
                for page_num, page in enumerate(pdf.pages[:max_pages]):
                    try:
                        # Extract text with layout preservation
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            # Clean and format text
                            cleaned_text = self._clean_extracted_text(page_text)
                            if cleaned_text:
                                text_parts.append(f"<!-- Page {page_num + 1} -->")
                                text_parts.append(cleaned_text)
                                text_parts.append("")  # Page separator
                        # Extract tables if present
                        tables = page.extract_tables()
                        if tables:
                            for table_num, table in enumerate(tables):
                                if table:
                                    table_html = self._convert_table_to_html(table, page_num + 1, table_num + 1)
                                    text_parts.append(table_html)
                                    text_parts.append("")
                    except Exception as e:
                        logger.warning(f"Error processing page {page_num + 1}: {str(e)}")
                        continue
                if total_pages > max_pages:
                    text_parts.append(f"<p><em>Note: Showing first {max_pages} of {total_pages} pages for performance.</em></p>")
                extracted_text = "\n".join(text_parts)
                if extracted_text.strip():
                    return True, extracted_text
                else:
                    return False, "No text content found in PDF"
        except Exception as e:
            return False, f"pdfplumber extraction error: {str(e)}"

    def _extract_with_pypdf(self, pdf_stream: BytesIO, filename: str) -> Tuple[bool, str]:
        """Extract text using pypdf library."""
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_stream)
            # Check if PDF is encrypted
            if reader.is_encrypted:
                return False, "PDF is password protected"
            text_parts = []
            total_pages = len(reader.pages)
            # Limit processing to first 50 pages
            max_pages = min(total_pages, 50)
            for page_num in range(max_pages):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        cleaned_text = self._clean_extracted_text(page_text)
                        if cleaned_text:
                            text_parts.append(f"<!-- Page {page_num + 1} -->")
                            text_parts.append(cleaned_text)
                            text_parts.append("")
                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1} with pypdf: {str(e)}")
                    continue
            if total_pages > max_pages:
                text_parts.append(f"<p><em>Note: Showing first {max_pages} of {total_pages} pages for performance.</em></p>")
            extracted_text = "\n".join(text_parts)
            if extracted_text.strip():
                return True, extracted_text
            else:
                return False, "No text content found in PDF"
        except Exception as e:
            return False, f"pypdf extraction error: {str(e)}"

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and format extracted text."""
        if not text:
            return ""
        # Convert literal \n to actual newlines
        text = text.replace('\\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
        lines = [line.strip() for line in text.split('\n')]
        cleaned_lines = []
        for line in lines:
            # Remove lines that are too short or just whitespace/special chars
            if len(line) > 2 and not line.replace(' ', '').replace('-', '').replace('_', '').replace('*', '') == '':
                if not cleaned_lines or cleaned_lines[-1] != line:
                    cleaned_lines.append(line)
        # Wrap each cleaned line in <p>...</p> for HTML output
        return '\n'.join([f'<p>{line}</p>' for line in cleaned_lines])
    
    def _convert_table_to_html(self, table: list, page_num: int, table_num: int) -> str:
        """Convert extracted table to HTML."""
        if not table or not table[0]:
            return ""
        
        try:
            html_parts = [
                f'<div style="margin: 20px 0;">',
                f'<h4>Table {table_num} (Page {page_num})</h4>',
                '<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">',
            ]
            
            # Add header row
            if table[0]:
                html_parts.append('<thead><tr>')
                for cell in table[0]:
                    html_parts.append(f'<th style="border: 1px solid #ddd; padding: 6px; background: #f5f5f5;">{cell}</th>')
                html_parts.append('</tr></thead>')
            
            # Add data rows
            html_parts.append('<tbody>')
            for row in table[1:]:
                if row:
                    html_parts.append('<tr>')
                    for cell in row:
                        html_parts.append(f'<td style="border: 1px solid #ddd; padding: 6px;">{cell}</td>')
                    html_parts.append('</tr>')
            
            html_parts.extend(['</tbody>', '</table>', '</div>'])
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            logger.warning(f"Error converting table to HTML: {str(e)}")
            return f"<p><em>Table {table_num} (Page {page_num}) - conversion error</em></p>"
    
    def _format_pdf_content(self, content: str, filename: str, file_size: int, method: str) -> str:
        """Format extracted PDF content with metadata."""
        file_size_mb = file_size / (1024 * 1024)
        
        header = f'''<div style="border: 2px solid #2196f3; border-radius: 12px; padding: 20px; margin: 20px 0; 
                     background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);">
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <div style="font-size: 32px; margin-right: 15px;">📄</div>
        <div>
            <h2 style="color: #1976d2; margin: 0; font-size: 20px;">PDF Document Content</h2>
            <h3 style="color: #2d3748; margin: 5px 0 0 0; font-size: 16px;">{filename}</h3>
        </div>
    </div>
    <div style="background: white; padding: 12px; border-radius: 6px; border-left: 4px solid #2196f3;">
        <p style="margin: 0; font-size: 13px; color: #4a5568;"><strong>File Size:</strong> {file_size_mb:.1f} MB</p>
        <p style="margin: 4px 0 0 0; font-size: 13px; color: #4a5568;"><strong>Extraction Method:</strong> {method}</p>
        <p style="margin: 4px 0 0 0; font-size: 13px; color: #4a5568;"><strong>Content Length:</strong> {len(content):,} characters</p>
    </div>
</div>

<div style="margin: 20px 0;">
{content}
</div>'''
        
        return header
    
    def _create_enhanced_placeholder(self, filename: str, file_size: int, error_message: str) -> str:
        """Create enhanced placeholder when extraction fails."""
        file_size_mb = file_size / (1024 * 1024)
        
        return f'''<div style="border: 2px solid #ff9800; border-radius: 12px; padding: 30px; margin: 20px 0; 
                   background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); text-align: center;">
    <div style="font-size: 48px; margin-bottom: 15px;">📄</div>
    <h2 style="color: #ef6c00; margin-bottom: 10px; font-size: 24px;">PDF Processing Status</h2>
    <h3 style="color: #2d3748; margin-bottom: 15px; font-size: 18px;">{filename}</h3>
    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800;">
        <p style="margin: 0; font-size: 14px; color: #4a5568;"><strong>File Size:</strong> {file_size_mb:.1f} MB</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Status:</strong> Text extraction attempted</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #4a5568;"><strong>Issue:</strong> {error_message}</p>
    </div>
    <div style="background: #fff3e0; padding: 15px; border-radius: 8px; border: 1px solid #ffcc02;">
        <p style="color: #ef6c00; font-size: 14px; line-height: 1.5; margin: 0;">
            <strong>📋 Next Steps:</strong><br>
            • Try copying text from the original PDF<br>
            • Use a PDF-to-text converter tool<br>
            • Check if the PDF is image-based (scanned document)<br>
            • Ensure the PDF is not password protected
        </p>
    </div>
</div>'''