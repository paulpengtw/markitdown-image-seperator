#!/usr/bin/env python3
"""
Test script for the Enhanced PDF Converter

This script demonstrates how to use the enhanced PDF converter to extract
figures and tables from academic PDFs with an interactive selection interface.
"""

import os
import sys
from pathlib import Path

# Add the markitdown package to the path
markitdown_path = Path(__file__).parent / "markitdown-image-seperator/packages/markitdown/src"
sys.path.insert(0, str(markitdown_path))

from markitdown import MarkItDown
from markitdown.converters import EnhancedPdfConverter

def test_enhanced_pdf_converter():
    """Test the enhanced PDF converter with the sample PDF."""
    
    # Check if sample PDF exists
    sample_pdf = Path("./sample/unconverted-[name-of-paper].pdf")
    if not sample_pdf.exists():
        print(f"Sample PDF not found at: {sample_pdf}")
        print("Please ensure the sample PDF is in the correct location.")
        return False
    
    # Create output directory
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 Testing Enhanced PDF Converter")
    print(f"📄 Input PDF: {sample_pdf}")
    print(f"📁 Output Directory: {output_dir}")
    print("-" * 50)
    
    try:
        # Initialize MarkItDown with enhanced converter
        markitdown = MarkItDown()
        
        # Register the enhanced converter with higher priority
        enhanced_converter = EnhancedPdfConverter()
        markitdown.register_converter(enhanced_converter, priority=0.0)
        
        print("✅ Enhanced PDF converter registered")
        
        # Convert the PDF
        print("🔄 Starting PDF conversion...")
        result = markitdown.convert(
            str(sample_pdf),
            output_dir=str(output_dir)
        )
        
        print("✅ PDF conversion completed!")
        print(f"📝 Title: {result.title}")
        print(f"📄 Content length: {len(result.markdown)} characters")
        
        # Save the main content
        output_file = output_dir / "converted-output.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print(f"💾 Main content saved to: {output_file}")
        
        # Check what files were created
        print("\n📂 Generated files:")
        for file in sorted(output_dir.glob("*")):
            if file.is_file():
                print(f"  - {file.name} ({file.stat().st_size} bytes)")
        
        # Check images directory
        images_dir = output_dir / "images"
        if images_dir.exists():
            print(f"\n🖼️  Images extracted ({len(list(images_dir.glob('*')))} files):")
            for img in sorted(images_dir.glob("*")):
                print(f"  - {img.name}")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality without GUI (for headless testing)."""
    
    print("🔧 Testing basic functionality (no GUI)...")
    
    # Test imports
    try:
        from markitdown.converters import EnhancedPdfConverter
        print("✅ Import successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test converter instantiation
    try:
        converter = EnhancedPdfConverter()
        print("✅ Converter instantiation successful")
    except Exception as e:
        print(f"❌ Converter instantiation failed: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 Enhanced PDF Converter Test Suite")
    print("=" * 50)
    
    # Test 1: Basic functionality
    if not test_basic_functionality():
        print("❌ Basic functionality test failed")
        return 1
    
    # Test 2: Full converter test
    if not test_enhanced_pdf_converter():
        print("❌ Full converter test failed")
        return 1
    
    print("\n🎉 All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())