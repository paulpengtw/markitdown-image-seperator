import sys
import io
import os
import re
import tempfile
from pathlib import Path
from typing import BinaryIO, Any, List, Tuple, Optional, Dict
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo
from .._exceptions import MissingDependencyException, MISSING_DEPENDENCY_MESSAGE


# Try loading optional (but in this case, required) dependencies
# Save reporting of any exceptions for later
_dependency_exc_info = None
try:
    import pdfminer
    import pdfminer.high_level
    import fitz  # PyMuPDF
except ImportError:
    # Preserve the error and stack trace for later
    _dependency_exc_info = sys.exc_info()


ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/pdf",
    "application/x-pdf",
]

ACCEPTED_FILE_EXTENSIONS = [".pdf"]


class PDFImageExtractor:
    """Handles PDF image and figure extraction with interactive selection."""
    
    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Store detected figures/tables for interactive selection
        self.detected_items: List[Dict] = []
        self.selected_items: List[Dict] = []
        
    def detect_figures_and_tables(self) -> List[Dict]:
        """Detect text references to figures, images, and tables in the PDF."""
        doc = fitz.open(self.pdf_path)
        detected_items = []
        
        # Patterns to match figure/table references
        patterns = [
            r'\bFigure\s+(\d+(?:\.\d+)?)\b',  # Figure 1, Figure 2.1, etc.
            r'\bImage\s+(\d+(?:\.\d+)?)\b',   # Image 1, Image 2.1, etc.
            r'\bTable\s+(\d+(?:\.\d+)?)\b',   # Table 1, Table 2.1, etc.
        ]
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Find all references to figures, images, and tables
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    ref_type = match.group(0).split()[0].lower()  # figure, image, or table
                    ref_number = match.group(1)  # the number part
                    
                    # Create a proper name based on actual text
                    proper_name = f"{ref_type}{ref_number}"
                    
                    # Check if we already found this reference
                    if not any(item['suggested_name'] == proper_name for item in detected_items):
                        detected_items.append({
                            "type": ref_type,
                            "page": page_num,
                            "bbox": None,  # Will be set by user selection
                            "suggested_name": proper_name,
                            "display_name": f"{ref_type.title()} {ref_number}",
                            "text_match": match.group(0)
                        })
        
        doc.close()
        
        # Sort by type and number for better organization
        def sort_key(item):
            # Extract numeric part for proper sorting
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', item['suggested_name'])
            if match:
                return (item['type'], float(match.group(1)))
            return (item['type'], 0)
        
        detected_items.sort(key=sort_key)
        
        self.detected_items = detected_items
        return detected_items
    
    
    def show_interactive_selection(self) -> List[Dict]:
        """Show interactive GUI for manual selection of figure/table regions."""
        if not self.detected_items:
            return []
        
        # Create main window
        root = tk.Tk()
        root.title("Manual Figure/Table Selection")
        root.geometry("1400x900")
        root.configure(bg="white")
        
        selected_items = []
        current_page = 0
        current_selection = None
        selection_start = None
        selection_rect = None
        
        # Open PDF for preview
        doc = fitz.open(self.pdf_path)
        
        def render_page(page_num):
            """Render PDF page as image."""
            page = doc[page_num]
            
            # Render page as image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL image
            pil_img = Image.open(io.BytesIO(img_data))
            return pil_img
        
        # Create UI elements
        frame = tk.Frame(root, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Page navigation
        nav_frame = tk.Frame(frame, bg="white")
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(nav_frame, text="Page:", bg="white", fg="black").pack(side=tk.LEFT)
        page_var = tk.StringVar(value=str(current_page + 1))
        page_entry = tk.Entry(nav_frame, textvariable=page_var, width=5, bg="white", fg="black")
        page_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(nav_frame, text=f"/ {len(doc)}", bg="white", fg="black").pack(side=tk.LEFT)
        
        # Status label
        status_label = tk.Label(nav_frame, text="Select an item from the list, then draw a rectangle around it on the PDF", 
                               fg="blue", bg="white")
        status_label.pack(side=tk.LEFT, padx=20)
        
        # Main content area
        content_frame = tk.Frame(frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # PDF display
        canvas_frame = tk.Frame(content_frame, bg="white")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        scrollbar_v = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview, bg="white")
        scrollbar_h = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview, bg="white")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Selection panel
        selection_frame = tk.Frame(content_frame, width=350, bg="white")
        selection_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        selection_frame.pack_propagate(False)
        
        tk.Label(selection_frame, text="Found References:", font=("Arial", 12, "bold"), bg="white", fg="black").pack(anchor=tk.W)
        
        # List of detected text references
        refs_listbox = tk.Listbox(selection_frame, selectmode=tk.SINGLE, height=10, bg="white", fg="black")
        refs_listbox.pack(fill=tk.X, pady=5)
        
        # Update the list with detected references
        def update_refs_list():
            refs_listbox.delete(0, tk.END)
            for item in self.detected_items:
                status = "✓" if item in selected_items else "○"
                refs_listbox.insert(tk.END, f"{status} {item['display_name']} (Page {item['page']+1})")
        
        tk.Label(selection_frame, text="Selected Items:", font=("Arial", 12, "bold"), bg="white", fg="black").pack(anchor=tk.W, pady=(10, 0))
        
        # List of selected items
        selected_listbox = tk.Listbox(selection_frame, selectmode=tk.SINGLE, height=8, bg="white", fg="black")
        selected_listbox.pack(fill=tk.X, pady=5)
        
        def update_selected_list():
            selected_listbox.delete(0, tk.END)
            for item in selected_items:
                selected_listbox.insert(tk.END, f"{item['display_name']} (Page {item['page']+1})")
        
        def get_current_ref():
            """Get the currently selected reference."""
            selection = refs_listbox.curselection()
            if selection:
                return self.detected_items[selection[0]]
            return None
        
        def on_canvas_click(event):
            """Handle mouse click on canvas."""
            nonlocal selection_start, current_selection, selection_rect
            
            current_ref = get_current_ref()
            if not current_ref:
                messagebox.showwarning("No Selection", "Please select a reference from the list first", parent=root)
                return
            
            if current_ref in selected_items:
                # Allow reselection - remove from selected items first
                selected_items.remove(current_ref)
                update_refs_list()
                update_selected_list()
                status_label.config(text=f"Reselecting {current_ref['display_name']} - drag to create rectangle")
            else:
                status_label.config(text=f"Selecting {current_ref['display_name']} - drag to create rectangle")
            
            # Clear any existing selection rectangle
            if selection_rect:
                canvas.delete(selection_rect)
                selection_rect = None
            
            # Start new selection
            selection_start = (canvas.canvasx(event.x), canvas.canvasy(event.y))
            current_selection = current_ref
        
        def on_canvas_drag(event):
            """Handle mouse drag on canvas."""
            nonlocal selection_rect
            
            if selection_start and current_selection:
                # Remove previous rectangle
                if selection_rect:
                    canvas.delete(selection_rect)
                
                # Draw new rectangle
                x1, y1 = selection_start
                x2, y2 = canvas.canvasx(event.x), canvas.canvasy(event.y)
                selection_rect = canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
        
        def on_canvas_release(event):
            """Handle mouse release on canvas."""
            nonlocal selection_start, current_selection, selection_rect
            
            if selection_start and current_selection:
                # Calculate final coordinates
                x1, y1 = selection_start
                x2, y2 = canvas.canvasx(event.x), canvas.canvasy(event.y)
                
                # Ensure proper order
                if x1 > x2:
                    x1, x2 = x2, x1
                if y1 > y2:
                    y1, y2 = y2, y1
                
                # Only proceed if we have a meaningful rectangle
                if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                    # Convert canvas coordinates to PDF coordinates
                    # Account for 2x zoom factor
                    pdf_bbox = fitz.Rect(x1/2, y1/2, x2/2, y2/2)
                    
                    # Add to selected items
                    current_selection["bbox"] = pdf_bbox
                    current_selection["final_name"] = current_selection["suggested_name"]
                    selected_items.append(current_selection)
                    
                    # Update displays
                    update_refs_list()
                    update_selected_list()
                    
                    status_label.config(text="Selection added! Select another item or finish.")
                else:
                    # Rectangle too small, clear it
                    if selection_rect:
                        canvas.delete(selection_rect)
                    status_label.config(text="Rectangle too small. Try again with a larger selection.")
                
                # Reset selection
                selection_start = None
                current_selection = None
                selection_rect = None
        
        # Bind canvas events
        canvas.bind("<Button-1>", on_canvas_click)
        canvas.bind("<B1-Motion>", on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", on_canvas_release)
        
        def update_display():
            nonlocal current_page, selection_rect
            try:
                new_page = int(page_var.get()) - 1
                if 0 <= new_page < len(doc):
                    current_page = new_page
                    img = render_page(current_page)
                    
                    # Resize for display
                    display_img = img.copy()
                    # Don't thumbnail - keep original size for precise selection
                    
                    photo = ImageTk.PhotoImage(display_img)
                    canvas.delete("all")  # This clears all rectangles too
                    selection_rect = None  # Reset the rectangle reference
                    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    canvas.image = photo  # Keep a reference
                    
                    update_refs_list()
                    update_selected_list()
            except ValueError:
                pass
        
        def remove_selected():
            """Remove selected item from the list."""
            selection = selected_listbox.curselection()
            if selection:
                item_to_remove = selected_items[selection[0]]
                selected_items.remove(item_to_remove)
                update_refs_list()
                update_selected_list()
                status_label.config(text="Item removed from selection")
        
        def finish_selection():
            root.quit()
        
        # Buttons
        btn_frame = tk.Frame(selection_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="Remove Selected", command=remove_selected, bg="white", fg="black").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Previous Page", 
                 command=lambda: [page_var.set(str(max(1, int(page_var.get()) - 1))), update_display()], 
                 bg="white", fg="black").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Next Page", 
                 command=lambda: [page_var.set(str(min(len(doc), int(page_var.get()) + 1))), update_display()], 
                 bg="white", fg="black").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Finish Selection", command=finish_selection, bg="green", fg="white").pack(fill=tk.X, pady=5)
        
        # Instructions
        instructions = """
INSTRUCTIONS:
1. Select a reference from the 'Found References' list
2. Navigate to the correct page if needed
3. Click and drag to draw a rectangle around the figure/table
4. Repeat for all items you want to extract
5. Click 'Finish Selection' when done
"""
        instruction_label = tk.Label(selection_frame, text=instructions, justify=tk.LEFT, 
                                   font=("Arial", 9), fg="gray", bg="white")
        instruction_label.pack(pady=10)
        
        # Bind events
        page_entry.bind('<Return>', lambda e: update_display())
        
        # Initial display
        update_display()
        
        # Run the GUI
        root.mainloop()
        root.destroy()
        doc.close()
        
        self.selected_items = selected_items
        return selected_items
    
    def extract_selected_items(self) -> Dict[str, str]:
        """Extract the selected items as images and return filename mappings."""
        if not self.selected_items:
            return {}
        
        doc = fitz.open(self.pdf_path)
        filename_map = {}
        
        for item in self.selected_items:
            try:
                page = doc[item["page"]]
                bbox = item["bbox"]
                final_name = item.get("final_name", item["suggested_name"])
                
                if not bbox:
                    print(f"Warning: No bbox for {final_name}, skipping")
                    continue
                
                # Render the selected region as high-resolution image
                mat = fitz.Matrix(3.0, 3.0)  # High resolution for all types
                pix = page.get_pixmap(matrix=mat, clip=bbox)
                img_bytes = pix.tobytes("png")
                filename = f"{final_name}.png"
                
                # Save image
                filepath = os.path.join(self.images_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
                
                filename_map[final_name] = f"./images/{filename}"
                
            except Exception as e:
                print(f"Error extracting {item}: {e}")
                continue
        
        doc.close()
        return filename_map


class EnhancedPdfConverter(DocumentConverter):
    """
    Enhanced PDF converter that extracts figures/tables and creates organized markdown output.
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        # Check the dependencies
        if _dependency_exc_info is not None:
            raise MissingDependencyException(
                MISSING_DEPENDENCY_MESSAGE.format(
                    converter=type(self).__name__,
                    extension=".pdf",
                    feature="pdf-enhanced",
                )
            ) from _dependency_exc_info[1].with_traceback(_dependency_exc_info[2])

        # Get output directory from kwargs
        output_dir = kwargs.get("output_dir")
        if not output_dir:
            # Create a temporary directory
            output_dir = tempfile.mkdtemp(prefix="markitdown_pdf_")
        
        # Create output directory structure
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save PDF to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(file_stream.read())
            temp_pdf_path = temp_pdf.name
        
        try:
            # Extract basic text
            file_stream.seek(0)
            basic_text = pdfminer.high_level.extract_text(file_stream)
            
            # Initialize image extractor
            extractor = PDFImageExtractor(temp_pdf_path, str(output_dir))
            
            # Detect figures and tables
            detected_items = extractor.detect_figures_and_tables()
            
            # Show interactive selection if items were detected
            selected_items = []
            if detected_items:
                try:
                    selected_items = extractor.show_interactive_selection()
                except Exception as e:
                    print(f"Interactive selection failed: {e}")
                    # Fall back to auto-selection of all items
                    selected_items = detected_items
                    for item in selected_items:
                        item["final_name"] = item["suggested_name"]
            
            # Extract selected images
            filename_map = {}
            if selected_items:
                extractor.selected_items = selected_items
                filename_map = extractor.extract_selected_items()
            
            # Process the text and insert image references
            processed_text = self._process_text_with_images(basic_text, filename_map, selected_items)
            
            # Separate references section
            main_text, references_text = self._separate_references(processed_text)
            
            # Save references to separate file if found
            if references_text:
                # Get the base filename from stream_info
                base_name = "document"
                if stream_info.filename:
                    base_name = Path(stream_info.filename).stem
                elif stream_info.local_path:
                    base_name = Path(stream_info.local_path).stem
                
                references_file = output_dir / f"{base_name}-references-converted.md"
                with open(references_file, "w", encoding="utf-8") as f:
                    f.write(references_text)
                
                print(f"DEBUG: Created references file: {references_file}")
            else:
                print("DEBUG: No references text found, skipping references file creation")
            
            return DocumentConverterResult(
                markdown=main_text,
                title=self._extract_title(basic_text)
            )
            
        finally:
            # Clean up temporary PDF
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
    
    def _process_text_with_images(self, text: str, filename_map: Dict[str, str], selected_items: List[Dict]) -> str:
        """Insert image references into the text at appropriate locations."""
        if not filename_map or not selected_items:
            return text
        
        lines = text.split('\n')
        processed_lines = []
        
        # Create a mapping from selected items to their display names for better matching
        selected_items_map = {}
        for item in selected_items:
            final_name = item.get('final_name', item.get('suggested_name', ''))
            display_name = item.get('display_name', '')
            if final_name and display_name:
                selected_items_map[final_name] = display_name
        
        print(f"DEBUG: Selected items map: {selected_items_map}")
        print(f"DEBUG: Filename map: {filename_map}")
        
        for line in lines:
            processed_lines.append(line)
            
            # Look for figure/table references in the text
            for item_name, image_path in filename_map.items():
                if item_name in selected_items_map:
                    display_name = selected_items_map[item_name]
                    
                    # Create patterns to match both the display name and variations
                    patterns = [
                        rf'\b{re.escape(display_name)}\b',  # e.g., "Figure 1"
                        rf'\b{re.escape(display_name.lower())}\b',  # e.g., "figure 1"
                        rf'\b{re.escape(item_name)}\b',  # e.g., "figure1"
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Insert image reference after this line
                            alt_text = display_name
                            image_ref = f"\n![{alt_text}]({image_path})\n"
                            processed_lines.append(image_ref)
                            print(f"DEBUG: Inserted image reference for {display_name}")
                            break
        
        return '\n'.join(processed_lines)
    
    def _separate_references(self, text: str) -> Tuple[str, str]:
        """Separate the references section from the main text."""
        # Look for common reference section markers
        ref_patterns = [
            r'\n\s*REFERENCES\s*\n',
            r'\n\s*References\s*\n',
            r'\n\s*BIBLIOGRAPHY\s*\n',
            r'\n\s*Bibliography\s*\n',
        ]
        
        print(f"DEBUG: Searching for references section in text of length {len(text)}")
        
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                split_pos = match.start()
                main_text = text[:split_pos].strip()
                references_text = text[split_pos:].strip()
                print(f"DEBUG: Found references section with pattern: {pattern}")
                print(f"DEBUG: References section length: {len(references_text)}")
                return main_text, references_text
        
        # No references section found
        print("DEBUG: No references section found")
        return text, ""
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract title from the beginning of the text."""
        lines = text.strip().split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 200:  # Reasonable title length
                # Skip if it looks like metadata
                if not any(marker in line.lower() for marker in ['doi:', 'arxiv:', 'volume', 'page']):
                    return line
        return None