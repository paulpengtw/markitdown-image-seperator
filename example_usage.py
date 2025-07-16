#!/usr/bin/env python3
"""
Example usage of the Enhanced PDF Converter

This script shows various ways to use the enhanced PDF converter
for extracting figures and tables from academic PDFs.
"""

import os
import sys
from pathlib import Path

# Add the markitdown package to the path
markitdown_path = Path(__file__).parent / "markitdown-image-seperator/packages/markitdown/src"
sys.path.insert(0, str(markitdown_path))

from markitdown import MarkItDown
from markitdown.converters import EnhancedPdfConverter

def basic_usage():
    """Basic usage example with interactive selection."""
    
    print("📚 Basic Usage Example")
    print("-" * 30)
    
    # Initialize MarkItDown with enhanced converter
    markitdown = MarkItDown()
    
    # Register the enhanced converter (replaces default PDF converter)
    enhanced_converter = EnhancedPdfConverter()
    markitdown.register_converter(enhanced_converter, priority=0.0)
    
    # Convert PDF with interactive selection
    output_dir = "./paper_output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        result = markitdown.convert(
            "research_paper.pdf",  # Replace with your PDF path
            output_dir=output_dir
        )
        
        print(f"✅ Conversion completed!")
        print(f"📝 Title: {result.title}")
        print(f"📄 Content length: {len(result.markdown)} characters")
        
        # Save the main content
        with open(f"{output_dir}/converted.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print(f"💾 Output saved to: {output_dir}/")
        
    except FileNotFoundError:
        print("❌ research_paper.pdf not found - please provide a valid PDF path")
    except Exception as e:
        print(f"❌ Error: {e}")

def batch_processing():
    """Example of batch processing multiple PDFs."""
    
    print("\n📦 Batch Processing Example")
    print("-" * 30)
    
    import glob
    
    # Initialize converter
    markitdown = MarkItDown()
    enhanced_converter = EnhancedPdfConverter()
    markitdown.register_converter(enhanced_converter, priority=0.0)
    
    # Process all PDFs in a directory
    pdf_files = glob.glob("papers/*.pdf")
    
    if not pdf_files:
        print("❌ No PDF files found in 'papers/' directory")
        return
    
    for pdf_file in pdf_files:
        paper_name = Path(pdf_file).stem
        output_dir = f"converted/{paper_name}"
        
        try:
            result = markitdown.convert(pdf_file, output_dir=output_dir)
            print(f"✅ Processed: {paper_name}")
            
            # Save main content
            with open(f"{output_dir}/{paper_name}-converted.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
                
        except Exception as e:
            print(f"❌ Failed to process {paper_name}: {e}")

def advanced_configuration():
    """Example with advanced configuration options."""
    
    print("\n⚙️  Advanced Configuration Example")
    print("-" * 30)
    
    # Initialize with custom configuration
    markitdown = MarkItDown()
    enhanced_converter = EnhancedPdfConverter()
    markitdown.register_converter(enhanced_converter, priority=0.0)
    
    # Custom configuration
    config = {
        "output_dir": "./advanced_output",
        "min_image_size": (100, 100),      # Minimum image dimensions
        "image_resolution_factor": 3.0,    # Higher resolution extraction
        "auto_select_all": False,          # Use interactive selection
    }
    
    os.makedirs(config["output_dir"], exist_ok=True)
    
    try:
        result = markitdown.convert("research_paper.pdf", **config)
        print(f"✅ Advanced conversion completed!")
        
        # Save with custom naming
        base_name = "research_paper"
        output_dir = Path(config["output_dir"])
        
        # Main content
        with open(output_dir / f"{base_name}-converted.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print(f"💾 Advanced output saved to: {config['output_dir']}/")
        
    except FileNotFoundError:
        print("❌ research_paper.pdf not found - please provide a valid PDF path")
    except Exception as e:
        print(f"❌ Error: {e}")

def headless_mode():
    """Example of headless mode (auto-select all items)."""
    
    print("\n🤖 Headless Mode Example")
    print("-" * 30)
    
    markitdown = MarkItDown()
    enhanced_converter = EnhancedPdfConverter()
    markitdown.register_converter(enhanced_converter, priority=0.0)
    
    # Auto-select all detected items (no GUI)
    config = {
        "output_dir": "./headless_output",
        "auto_select_all": True,  # Skip interactive selection
    }
    
    os.makedirs(config["output_dir"], exist_ok=True)
    
    try:
        result = markitdown.convert("research_paper.pdf", **config)
        print(f"✅ Headless conversion completed!")
        print(f"📄 Auto-extracted all detected figures and tables")
        
        with open(f"{config['output_dir']}/converted.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print(f"💾 Headless output saved to: {config['output_dir']}/")
        
    except FileNotFoundError:
        print("❌ research_paper.pdf not found - please provide a valid PDF path")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    
    print("🔍 Checking Dependencies")
    print("-" * 30)
    
    dependencies = [
        ("pdfminer.six", "pdfminer"),
        ("pymupdf", "fitz"),
        ("pillow", "PIL"),
        ("tkinter", "tkinter"),
    ]
    
    all_good = True
    
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name}")
        except ImportError:
            print(f"❌ {dep_name} - Install with: pip install {dep_name}")
            all_good = False
    
    if all_good:
        print("\n🎉 All dependencies are installed!")
    else:
        print("\n❌ Some dependencies are missing. Please install them before proceeding.")
    
    return all_good

def main():
    """Main function demonstrating all usage patterns."""
    
    print("🧪 Enhanced PDF Converter - Usage Examples")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n⚠️  Please install missing dependencies before running examples.")
        return 1
    
    # Run examples
    try:
        basic_usage()
        batch_processing()
        advanced_configuration()
        headless_mode()
        
        print("\n🎉 All examples completed!")
        print("\n📋 Next steps:")
        print("1. Replace 'research_paper.pdf' with your actual PDF file")
        print("2. Run the script to see the interactive selection GUI")
        print("3. Check the output directories for extracted images and markdown")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())