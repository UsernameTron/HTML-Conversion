#!/usr/bin/env python3
"""
Comprehensive Application Tester
===============================

Tests all critical components of the HTML Converter application to identify
real issues and verify fixes work correctly.
"""

import sys
import os
import traceback
from pathlib import Path
import importlib
import tempfile
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import streamlit for testing
try:
    import streamlit as st
except ImportError:
    st = None

class ComprehensiveTester:
    def __init__(self):
        self.results = []
        self.failures = []
        self.critical_failures = []
    
    def log_result(self, message, is_critical=False):
        """Log a test result"""
        if message.startswith("❌"):
            if is_critical:
                self.critical_failures.append(message)
            else:
                self.failures.append(message)
        else:
            self.results.append(message)
    
    def test_imports(self):
        """Test all critical imports"""
        print("🔍 Testing Module Imports...")
        
        imports_to_test = [
            ('utils.cache_manager', 'StreamlitCacheManager'),
            ('utils.performance_monitor', 'monitor_performance'), 
            ('services.file_processor', 'FileProcessor'),
            ('services.html_generator', 'HTMLGenerator'),
            ('ui.main_page', 'MainPage'),
            ('ui.pages.template_page', 'TemplatePage'),
            ('models.style_models', 'StyleConfig'),
            ('services.document_processors.pdf_processor', 'PDFProcessor'),
            ('utils.css_sanitizer', 'sanitize_css'),
        ]
        
        for module_name, class_or_func in imports_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_or_func):
                    self.log_result(f"✅ {module_name}.{class_or_func}")
                else:
                    self.log_result(f"❌ {module_name}: Missing {class_or_func}", is_critical=True)
            except ImportError as e:
                self.log_result(f"❌ {module_name}: Import failed - {e}", is_critical=True)
            except Exception as e:
                self.log_result(f"❌ {module_name}: Unexpected error - {e}")
    
    def test_pdf_processing(self):
        """Test PDF processing functionality with real issues"""
        print("📄 Testing PDF Processing...")
        
        try:
            from services.document_processors.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            
            # Test 1: Text cleaning with literal newlines (the actual issue)
            test_text_with_literals = "Sample\\nText\\nWith\\nLiteral\\nNewlines"
            cleaned = processor._clean_extracted_text(test_text_with_literals)
            
            if "\\n" in cleaned:
                self.log_result("❌ PDF processor still contains literal \\n characters", is_critical=True)
            else:
                self.log_result("✅ PDF processor newline handling correct")
            
            # Test 2: Check for duplicate line bug
            test_simple = "This is a test line"
            cleaned_simple = processor._clean_extracted_text(test_simple)
            line_count = cleaned_simple.count("This is a test line")
            
            if line_count > 1:
                self.log_result("❌ PDF processor has duplicate line bug", is_critical=True)
            else:
                self.log_result("✅ PDF processor no duplicate lines")
            
            # Test 3: HTML output formatting
            if "<p>" in cleaned and "</p>" in cleaned:
                self.log_result("✅ PDF processor generates proper HTML paragraphs")
            else:
                self.log_result("❌ PDF processor not generating proper HTML", is_critical=True)
                
        except Exception as e:
            self.log_result(f"❌ PDF processor test failed: {e}", is_critical=True)
    
    def test_streamlit_compatibility(self):
        """Test Streamlit compatibility and API usage"""
        print("🌊 Testing Streamlit Compatibility...")
        
        try:
            import streamlit as st
            
            # Check for deprecated vs new API
            if hasattr(st, 'experimental_rerun'):
                self.log_result("⚠️ Using deprecated st.experimental_rerun")
            
            if hasattr(st, 'rerun'):
                self.log_result("✅ Streamlit rerun available")
            else:
                self.log_result("❌ Streamlit rerun not available", is_critical=True)
            
            # Check column functionality
            try:
                # This should not raise an error
                cols = st.columns(3)
                self.log_result("✅ Streamlit columns working")
            except Exception as e:
                self.log_result(f"❌ Streamlit columns error: {e}")
                
        except Exception as e:
            self.log_result(f"❌ Streamlit test failed: {e}", is_critical=True)
    
    def test_css_sanitizer(self):
        """Test CSS sanitizer compatibility"""
        print("🎨 Testing CSS Sanitizer...")
        
        try:
            from utils.css_sanitizer import sanitize_css
            
            test_css = """
            body { color: red; }
            .test { background: blue; }
            """
            
            sanitized = sanitize_css(test_css)
            
            if sanitized and len(sanitized) > 0:
                self.log_result("✅ CSS sanitizer working")
            else:
                self.log_result("❌ CSS sanitizer returned empty result", is_critical=True)
                
        except Exception as e:
            self.log_result(f"❌ CSS sanitizer test failed: {e}", is_critical=True)
    
    def test_file_processing(self):
        """Test file processing functionality"""
        print("📁 Testing File Processing...")
        
        try:
            from services.file_processor import FileProcessor
            
            processor = FileProcessor()
            
            # Test with a simple mock file object
            class MockFile:
                def __init__(self, content, name):
                    self.content = content
                    self.name = name
                    self.size = len(content)
                
                def read(self):
                    return self.content
                
                def getvalue(self):
                    return self.content
            
            # Test with simple text content
            mock_file = MockFile(b"Test content", "test.txt")
            
            # FileProcessor expects process_file method
            if hasattr(processor, 'process_file'):
                self.log_result("✅ File processor has correct method")
            else:
                self.log_result("❌ File processor missing process_file method")
            
        except Exception as e:
            self.log_result(f"❌ File processor test failed: {e}")
    
    def test_configuration_issues(self):
        """Test for configuration issues"""
        print("⚙️ Testing Configuration...")
        
        # Check if CORS configuration issue exists
        dockerfile_path = project_root / "Dockerfile"
        if dockerfile_path.exists():
            content = dockerfile_path.read_text()
            
            if "enableCORS = false" in content and "enableXsrfProtection = true" in content:
                self.log_result("❌ CORS/XSRF configuration conflict in Dockerfile", is_critical=True)
            elif "enableCORS = true" in content:
                self.log_result("✅ CORS configuration correct")
            else:
                self.log_result("⚠️ Could not verify CORS configuration")
        
        # Check for missing __init__.py files
        critical_dirs = [
            project_root / "src" / "ui" / "pages",
            project_root / "src" / "services" / "document_processors",
        ]
        
        for dir_path in critical_dirs:
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                self.log_result(f"❌ Missing __init__.py in {dir_path.relative_to(project_root)}")
            else:
                self.log_result(f"✅ __init__.py exists in {dir_path.relative_to(project_root)}")
    
    def test_dependencies(self):
        """Test critical dependencies"""
        print("📦 Testing Dependencies...")
        
        critical_deps = [
            'streamlit',
            'pdfplumber', 
            'bleach',
            'redis',
            'psutil'
        ]
        
        for dep in critical_deps:
            try:
                importlib.import_module(dep)
                self.log_result(f"✅ {dep} available")
            except ImportError:
                if dep in ['pdfplumber']:
                    self.log_result(f"❌ {dep} missing - PDF processing will fail", is_critical=True)
                else:
                    self.log_result(f"⚠️ {dep} missing")
    
    def run_all_tests(self):
        """Run all tests and report results"""
        print("🔍 COMPREHENSIVE APPLICATION TESTING")
        print("=" * 60)
        print(f"Testing application at: {project_root}")
        print("")
        
        # Run all test categories
        self.test_dependencies()
        print()
        self.test_imports()
        print()
        self.test_pdf_processing()
        print()
        self.test_streamlit_compatibility()
        print()
        self.test_css_sanitizer()
        print()
        self.test_file_processing()
        print()
        self.test_configuration_issues()
        
        # Report results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n✅ PASSED TESTS ({len(self.results)}):")
        for result in self.results:
            print(f"  {result}")
        
        if self.failures:
            print(f"\n⚠️ NON-CRITICAL ISSUES ({len(self.failures)}):")
            for failure in self.failures:
                print(f"  {failure}")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"  {failure}")
            
            print(f"\n🚨 APPLICATION STATUS: BROKEN")
            print(f"Critical issues must be fixed before application will work properly.")
            return False
        elif self.failures:
            print(f"\n⚠️ APPLICATION STATUS: DEGRADED")
            print(f"Application may work but has issues that should be addressed.")
            return True
        else:
            print(f"\n🎉 APPLICATION STATUS: HEALTHY")
            print(f"All tests passed successfully!")
            return True

def main():
    """Run comprehensive testing"""
    tester = ComprehensiveTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n" + "=" * 60)
        print("🛠️ RECOMMENDED ACTIONS:")
        print("1. Fix critical import issues")
        print("2. Fix PDF processing newline handling")
        print("3. Update Streamlit API usage")
        print("4. Fix configuration conflicts")
        print("5. Re-run tests to verify fixes")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
