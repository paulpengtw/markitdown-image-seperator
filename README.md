# Enhanced MarkItDown PDF Converter with Figure/Table Extraction

This project enhances the standard `markitdown` library to extract figures and tables from academic PDFs while maintaining proper references in the converted markdown output.

## Features

- **Automatic Figure/Table Detection**: Automatically detects images, figures, and table-like structures in PDFs
- **Interactive Selection Interface**: GUI tool for manually selecting and refining detected items
- **Organized Output Structure**: Creates clean folder structure with separate images directory
- **Smart Image References**: Automatically inserts markdown image references in appropriate locations
- **References Separation**: Extracts REFERENCES section to a separate markdown file
- **High-Quality Image Extraction**: Saves figures and tables as high-resolution PNG images

## Installation

### Prerequisites

```bash
# Install enhanced dependencies
pip install pymupdf pillow tkinter

# Install markitdown with PDF support
pip install "markitdown[pdf]"
```

### Setup Enhanced Converter

1. Clone the enhanced markitdown repository:
```bash
git clone /path/to/markitdown-image-seperator
cd markitdown-image-seperator/packages/markitdown
```

2. Install in development mode:
```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from markitdown import MarkItDown
from markitdown.converters import EnhancedPdfConverter
import os

# Initialize MarkItDown with enhanced PDF converter
markitdown = MarkItDown()

# Replace the default PDF converter with enhanced version
markitdown.register_converter(EnhancedPdfConverter(), priority=0.0)

# Convert PDF with figure extraction
output_dir = "./converted_paper"
os.makedirs(output_dir, exist_ok=True)

result = markitdown.convert(
    "research_paper.pdf",
    output_dir=output_dir
)

# The result will contain the main content
print(result.markdown)
```

### Command Line Usage

```bash
# Create output directory
mkdir paper_output

# Convert PDF with enhanced features
python -m markitdown research_paper.pdf --output-dir paper_output --extract-images
```

## How It Works

### 1. Text Reference Detection Phase
- **Text Analysis**: Scans PDF text for references like "Figure 1", "Table 2", "Image 3"
- **Smart Numbering**: Uses actual numbering from the PDF text (e.g., "Figure 2.1", "Table A.3")
- **Reference Parsing**: Supports various formats including decimal numbering

### 2. Interactive Manual Selection Phase
When text references are found, an interactive GUI window opens:

```
┌─────────────────────────────────────────────────────────────┐
│ Manual Figure/Table Selection                               │
├─────────────────────────────────────────────────────────────┤
│ Page: [1] / 10          [Previous] [Next]                  │
├─────────────────────────────────────────────────────────────┤
│                    │ Found References:                      │
│   PDF Preview      │ ○ Figure 1 (Page 2)                   │
│   (click & drag    │ ○ Table 1 (Page 3)                    │
│    to select)      │ ✓ Figure 2 (Page 4)                   │
│                    │                                        │
│                    │ Selected Items:                        │
│                    │ • Figure 2 (Page 4)                   │
│                    │                                        │
│                    │ [Remove Selected]                      │
│                    │ [Finish Selection]                     │
└─────────────────────────────────────────────────────────────┘
```

**Interactive Features:**
- **Text-Based Detection**: Only finds items explicitly mentioned in text
- **Manual Rectangle Selection**: Click and drag to select figure/table regions
- **Precise Control**: You decide exactly what area to extract
- **Visual Feedback**: Real-time rectangle drawing with red outline
- **Page Navigation**: Jump to any page to find the referenced item

### 3. Extraction and Processing Phase
- **High-Quality Extraction**: Extracts selected items as PNG images at 3x resolution
- **Smart Placement**: Inserts image references near relevant text mentions
- **Reference Separation**: Moves REFERENCES section to separate file

## Output Structure

After processing, you'll get this organized structure:

```
paper_output/
├── research_paper-converted.md      # Main content with image references
├── research_paper-references-converted.md  # References section
└── images/
    ├── figure1.png                  # Extracted figure 1
    ├── table1.png                   # Extracted table 1
    ├── figure2.png                  # Extracted figure 2
    └── ...
```

### Example Output Content

**Main Markdown File (`research_paper-converted.md`):**
```markdown
# On the Dangers of Stochastic Parrots

## Abstract
The past 3 years of work in NLP have been characterized by...

## Introduction
One of the biggest trends in natural language processing...

![Table1](./images/table1.png)
Table 1: Overview of recent large language models

As shown in Table 1, the models have grown significantly...

![Figure1](./images/figure1.png)
Figure 1: GPT-3's response to the prompt

The example in Figure 1 illustrates GPT-3's ability...
```

**References File (`research_paper-references-converted.md`):**
```markdown
# REFERENCES

[1] Hussein M Adam, Robert D Bullard, and Elizabeth Bell. 2001. Faces of environmental racism...

[2] Chris Alberti, Kenton Lee, and Michael Collins. 2019. A BERT Baseline for the Natural Questions...
```

## Advanced Configuration

### Customizing Detection Sensitivity

```python
converter = EnhancedPdfConverter()

# Configure detection parameters
config = {
    "min_image_size": (100, 100),      # Minimum image dimensions
    "min_table_rows": 3,               # Minimum rows for table detection
    "image_resolution_factor": 3.0,    # Extraction resolution multiplier
    "auto_select_all": False,          # Skip interactive selection
}

result = markitdown.convert("paper.pdf", **config)
```

### Batch Processing

```python
import glob
from pathlib import Path

# Process multiple PDFs
pdf_files = glob.glob("papers/*.pdf")

for pdf_file in pdf_files:
    paper_name = Path(pdf_file).stem
    output_dir = f"converted/{paper_name}"
    
    result = markitdown.convert(pdf_file, output_dir=output_dir)
    print(f"Processed: {paper_name}")
```

## Troubleshooting

### Common Issues

1. **GUI Not Appearing**
   ```bash
   # Install tkinter if missing
   sudo apt-get install python3-tk  # Ubuntu/Debian
   brew install python-tk           # macOS
   ```

2. **Low Image Quality**
   ```python
   # Increase resolution factor
   result = markitdown.convert("paper.pdf", image_resolution_factor=4.0)
   ```

3. **Missing Dependencies**
   ```bash
   pip install pymupdf pillow pdfminer.six
   ```

### Performance Notes

- **Large PDFs**: Processing may take several minutes for documents with many images
- **Memory Usage**: High-resolution extraction requires substantial RAM
- **Interactive Mode**: GUI requires display access (not suitable for headless servers)

## API Reference

### EnhancedPdfConverter

```python
class EnhancedPdfConverter(DocumentConverter):
    def convert(self, file_stream, stream_info, **kwargs):
        """
        Convert PDF with figure/table extraction.
        
        Args:
            file_stream: PDF file stream
            stream_info: File metadata
            output_dir: Directory for output files
            auto_select_all: Skip interactive selection
            image_resolution_factor: Image extraction quality
            min_image_size: Minimum dimensions for image detection
            min_table_rows: Minimum rows for table detection
        
        Returns:
            DocumentConverterResult with markdown content
        """
```

### PDFImageExtractor

```python
class PDFImageExtractor:
    def detect_figures_and_tables(self) -> List[Dict]:
        """Detect potential figures and tables in PDF."""
    
    def show_interactive_selection(self) -> List[Dict]:
        """Show GUI for manual selection."""
    
    def extract_selected_items(self) -> Dict[str, str]:
        """Extract selected items as images."""
```

## Contributing

To extend the functionality:

1. **Custom Detection Algorithms**: Modify `_detect_tables()` method
2. **Enhanced GUI**: Improve the interactive selection interface  
3. **Additional Formats**: Support for more figure/table types
4. **OCR Integration**: Add text recognition for scanned documents

## License

This project extends the MIT-licensed `markitdown` library with additional features for academic document processing.