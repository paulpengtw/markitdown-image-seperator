# Implementation Plan: Enhanced PDF Converter

## Phase 1: Core Dependencies Setup

### Required Dependencies
```bash
pip install pymupdf  # For PDF processing and image extraction
pip install pillow   # For image processing
pip install tkinter  # For GUI (usually included with Python)
```

### Files to Create/Modify
1. `_pdf_enhanced_converter.py` - Main enhanced converter
2. Update `__init__.py` to include the new converter
3. Add new dependencies to `pyproject.toml`

## Phase 2: Basic Implementation Structure

### Core Classes
1. **EnhancedPdfConverter** - Main converter class
2. **PDFImageExtractor** - Handles image/figure detection and extraction
3. **InteractiveSelector** - GUI for manual selection

### Key Methods
- `detect_figures_and_tables()` - Auto-detect items in PDF
- `show_interactive_selection()` - GUI for user selection
- `extract_selected_items()` - Extract as PNG images
- `_process_text_with_images()` - Insert markdown references
- `_separate_references()` - Split references section

## Phase 3: Testing Strategy

### Test Cases
1. **Basic PDF with images** - Test image extraction
2. **Academic paper with tables** - Test table detection
3. **Multi-page document** - Test page navigation
4. **PDF with references** - Test reference separation

### Expected Outputs
- Main markdown file with image references
- Separate references markdown file
- Images folder with extracted PNG files
- Proper folder structure

## Phase 4: Integration Points

### With Existing MarkItDown
- Register as alternative PDF converter
- Maintain compatibility with existing API
- Add optional parameters for configuration

### Command Line Interface
```bash
# Basic usage
markitdown paper.pdf --output-dir ./output --extract-images

# With configuration
markitdown paper.pdf --extract-images --min-image-size 100x100 --auto-select
```

## Phase 5: GUI Design

### Interactive Selection Window
```
┌─────────────────────────────────────────────────┐
│ PDF Figure/Table Selector                       │
├─────────────────────────────────────────────────┤
│ Page: [1] / 10    [Prev] [Next]                 │
├─────────────────┬───────────────────────────────┤
│                 │ Detected Items:               │
│   PDF Preview   │ ☐ Figure 1 (Page 1)         │
│   with boxes    │ ☐ Table 1 (Page 1)          │
│   around items  │ ☐ Figure 2 (Page 2)         │
│                 │                               │
│   Red = Images  │ [Add Selected]                │
│   Blue = Tables │ [Clear All]                   │
│                 │ [Custom Select]               │
│                 │ [Finish]                      │
└─────────────────┴───────────────────────────────┘
```

### Features
- Visual preview of PDF pages
- Colored boxes around detected items
- Checkbox selection of items
- Custom naming for each item
- Page navigation controls
- Manual rectangle selection (future)

## Phase 6: Advanced Features (Future)

### Planned Enhancements
1. **OCR Integration** - Extract text from image-based tables
2. **Custom Selection Areas** - Draw rectangles around custom regions
3. **Batch Processing** - Process multiple PDFs automatically
4. **Export Options** - Different image formats (PNG, JPG, SVG)
5. **Table Structure Recognition** - Convert tables to markdown tables

### Configuration Options
```python
config = {
    "image_resolution": 300,           # DPI for extracted images
    "min_image_size": (50, 50),       # Minimum size to detect
    "table_detection_sensitivity": 0.7, # How strict table detection is
    "auto_select_large_items": True,   # Auto-select items above threshold
    "output_format": "png",            # Image format
    "separate_references": True,       # Create separate references file
}
```

## Testing Checklist

### Before Implementation
- [ ] Verify all dependencies can be installed
- [ ] Test GUI functionality on target system
- [ ] Confirm PyMuPDF can open sample PDFs

### During Implementation
- [ ] Test with sample academic paper
- [ ] Verify image extraction quality
- [ ] Test interactive selection GUI
- [ ] Validate markdown output format
- [ ] Test reference separation

### After Implementation
- [ ] Test with various PDF types
- [ ] Verify folder structure creation
- [ ] Test batch processing capability
- [ ] Validate integration with existing markitdown

## Rollback Plan

If implementation fails:
1. Keep original `_pdf_converter.py` unchanged
2. Make enhanced converter opt-in only
3. Provide fallback to basic text extraction
4. Clear error messages for missing dependencies

## Success Metrics

1. **Functionality**: Successfully extracts figures/tables from academic PDFs
2. **Usability**: Interactive GUI is intuitive and responsive
3. **Quality**: Extracted images are high-quality and properly referenced
4. **Integration**: Works seamlessly with existing markitdown workflow
5. **Performance**: Processes typical academic papers in <2 minutes