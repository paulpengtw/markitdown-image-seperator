#!/usr/bin/env python3
"""
Test script for text-based figure/table detection

This script tests the new text-based detection logic that looks for
"Figure X", "Image X", and "Table X" references in PDF text.
"""

import os
import sys
import re
from pathlib import Path

# Add the markitdown package to the path
markitdown_path = Path(__file__).parent / "markitdown-image-seperator/packages/markitdown/src"
sys.path.insert(0, str(markitdown_path))

def test_regex_patterns():
    """Test the regex patterns for detecting figure/table references."""
    
    print("🧪 Testing Text Detection Patterns")
    print("-" * 40)
    
    # Test patterns
    patterns = [
        r'\bFigure\s+(\d+(?:\.\d+)?)\b',  # Figure 1, Figure 2.1, etc.
        r'\bImage\s+(\d+(?:\.\d+)?)\b',   # Image 1, Image 2.1, etc.
        r'\bTable\s+(\d+(?:\.\d+)?)\b',   # Table 1, Table 2.1, etc.
    ]
    
    # Test text samples
    test_texts = [
        "As shown in Figure 1, the results demonstrate...",
        "Table 2.1 shows the comparison between methods.",
        "Image 3 illustrates the concept clearly.",
        "See Figure 10 for more details.",
        "The data in Table 1 and Table 2 support our hypothesis.",
        "Figure 2.5 and Figure 2.6 show different aspects.",
        "This figure shows something (not a reference)",
        "table data is important (not a reference)",
        "In Figure1 we see... (no space, shouldn't match)",
        "Figure A.1 shows... (should this match?)"
    ]
    
    print("Testing patterns:")
    for i, pattern in enumerate(patterns):
        ref_type = ["Figure", "Image", "Table"][i]
        print(f"  {ref_type}: {pattern}")
    
    print("\nTesting on sample texts:")
    for text in test_texts:
        print(f"\nText: '{text}'")
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref_type = match.group(0).split()[0].lower()
                ref_number = match.group(1)
                proper_name = f"{ref_type}{ref_number}"
                print(f"  ✓ Found: {match.group(0)} -> {proper_name}")

def test_sorting_logic():
    """Test the sorting logic for detected references."""
    
    print("\n🔢 Testing Sorting Logic")
    print("-" * 40)
    
    # Sample detected items
    detected_items = [
        {"type": "table", "suggested_name": "table2"},
        {"type": "figure", "suggested_name": "figure1"},
        {"type": "figure", "suggested_name": "figure10"},
        {"type": "table", "suggested_name": "table1"},
        {"type": "image", "suggested_name": "image1"},
        {"type": "figure", "suggested_name": "figure2.1"},
        {"type": "figure", "suggested_name": "figure2.2"},
    ]
    
    def sort_key(item):
        # Extract numeric part for proper sorting
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', item['suggested_name'])
        if match:
            return (item['type'], float(match.group(1)))
        return (item['type'], 0)
    
    print("Before sorting:")
    for item in detected_items:
        print(f"  {item['suggested_name']}")
    
    detected_items.sort(key=sort_key)
    
    print("\nAfter sorting:")
    for item in detected_items:
        print(f"  {item['suggested_name']}")

def test_with_actual_pdf():
    """Test with the actual PDF converter if available."""
    
    print("\n📄 Testing with Actual PDF Detection")
    print("-" * 40)
    
    try:
        from markitdown.converters._pdf_enhanced_converter import PDFImageExtractor
        
        # Check if sample PDF exists
        sample_pdf = Path("./sample/unconverted-[name-of-paper].pdf")
        if not sample_pdf.exists():
            print("❌ Sample PDF not found - skipping actual PDF test")
            return
        
        # Create a temporary output directory
        output_dir = Path("./test_detection_output")
        output_dir.mkdir(exist_ok=True)
        
        # Test detection
        extractor = PDFImageExtractor(str(sample_pdf), str(output_dir))
        detected_items = extractor.detect_figures_and_tables()
        
        print(f"✅ Found {len(detected_items)} text references:")
        for item in detected_items:
            print(f"  - {item['display_name']} (Page {item['page']+1})")
            print(f"    Type: {item['type']}")
            print(f"    Suggested name: {item['suggested_name']}")
            print(f"    Text match: '{item['text_match']}'")
            print()
        
        if not detected_items:
            print("ℹ️  No references found - this might be expected if the PDF doesn't contain explicit Figure/Table references")
        
    except ImportError as e:
        print(f"❌ Cannot import enhanced converter: {e}")
    except Exception as e:
        print(f"❌ Error during PDF testing: {e}")

def main():
    """Run all tests."""
    
    print("🚀 Enhanced PDF Converter - Text Detection Tests")
    print("=" * 60)
    
    test_regex_patterns()
    test_sorting_logic()
    test_with_actual_pdf()
    
    print("\n🎉 Text detection tests completed!")
    print("\nNext steps:")
    print("1. Run the full converter with a PDF containing Figure/Table references")
    print("2. Use the manual selection GUI to draw rectangles around the referenced items")
    print("3. Check the extracted images and markdown output")

if __name__ == "__main__":
    main()