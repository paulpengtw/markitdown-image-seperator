#!/usr/bin/env python3
"""
Setup script for Enhanced PDF Converter dependencies

This script helps install all required dependencies for the enhanced PDF converter.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Enhanced PDF converter requires Python 3.10 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install all required dependencies."""
    print("\n📦 Installing Dependencies")
    print("-" * 30)
    
    # Core dependencies
    dependencies = [
        "pdfminer.six",
        "pymupdf",
        "pillow",
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def install_markitdown():
    """Install markitdown with enhanced PDF support."""
    print("\n📚 Installing Enhanced MarkItDown")
    print("-" * 30)
    
    markitdown_path = "./markitdown-image-seperator/packages/markitdown"
    
    if not os.path.exists(markitdown_path):
        print(f"❌ MarkItDown source not found at: {markitdown_path}")
        print("   Please ensure the markitdown-image-seperator directory exists")
        return False
    
    # Install in development mode with enhanced PDF support
    command = f"pip install -e '{markitdown_path}[pdf-enhanced]'"
    return run_command(command, "Installing enhanced MarkItDown")

def verify_installation():
    """Verify that all components are properly installed."""
    print("\n🔍 Verifying Installation")
    print("-" * 30)
    
    # Test imports
    test_imports = [
        ("pdfminer.six", "pdfminer"),
        ("PyMuPDF", "fitz"),
        ("Pillow", "PIL"),
        ("tkinter", "tkinter"),
    ]
    
    all_good = True
    
    for display_name, import_name in test_imports:
        try:
            __import__(import_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name} - {e}")
            all_good = False
    
    # Test enhanced converter import
    try:
        sys.path.insert(0, "./markitdown-image-seperator/packages/markitdown/src")
        from markitdown.converters import EnhancedPdfConverter
        print("✅ Enhanced PDF Converter")
    except ImportError as e:
        print(f"❌ Enhanced PDF Converter - {e}")
        all_good = False
    
    return all_good

def setup_test_environment():
    """Create test directories and files."""
    print("\n🏗️  Setting up Test Environment")
    print("-" * 30)
    
    # Create test directories
    test_dirs = [
        "./test_output",
        "./paper_output", 
        "./converted",
        "./papers",
    ]
    
    for directory in test_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create a simple test PDF info file
    test_info = """
# Test Setup Complete!

To test the enhanced PDF converter:

1. Place your PDF file in the current directory
2. Run: python example_usage.py
3. Or run: python test_enhanced_converter.py

## Example Commands:

```bash
# Basic usage with interactive selection
python example_usage.py

# Test with sample PDF
python test_enhanced_converter.py

# Install additional dependencies if needed
pip install pdfminer.six pymupdf pillow
```

## Output Structure:
- Main markdown file with image references
- Separate references markdown file  
- images/ folder with extracted figures and tables
"""
    
    with open("TEST_SETUP.md", "w") as f:
        f.write(test_info)
    
    print("✅ Created TEST_SETUP.md with instructions")

def main():
    """Main setup function."""
    print("🚀 Enhanced PDF Converter Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        return 1
    
    # Install markitdown
    if not install_markitdown():
        print("\n❌ MarkItDown installation failed")
        return 1
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        return 1
    
    # Setup test environment
    setup_test_environment()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Place a PDF file in the current directory")
    print("2. Run: python example_usage.py")
    print("3. Or run: python test_enhanced_converter.py")
    print("4. Check the generated output directories")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())