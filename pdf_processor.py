from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import tqdm
import re
from semantic_text_chunker import SemanticTextChunker


def pdf2html(pdf_path: Path) -> str:
    """Convert PDF to HTML using pdfminer"""
    html_path = pdf_path.with_suffix('.html')
    with pdf_path.open('rb') as fh, html_path.open('wb') as out:
        extract_text_to_fp(
            fh, out,
            laparams=LAParams(),
            output_type='html',
            codec='utf-8'
        )
    return html_path


def chunk_html_content(html_path: Path, source_pdf: str) -> list:
    """Parse HTML and create text chunks with metadata using DOM walking"""
    soup = BeautifulSoup(html_path.read_text(), 'lxml')
    
    chunks = []
    chunk_id = 0
    
    # Walk the DOM for semantic elements
    for node in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'table', 'div', 'span']):
        text = node.get_text(' ', strip=True)
        
        # Skip empty or very short chunks
        if len(text) < 20:
            continue
            
        # Skip page numbers and navigation elements
        if text.startswith('Page ') or (text.isdigit() and len(text) < 4):
            continue
        
        # Create metadata similar to your example
        meta = {
            "pdf_file": f"{source_pdf}.pdf",
            "page": node.get('data-page'),  # pdfminer writes this attr
            "tag": node.name,
            "hier": node.name + '|' + (node.parent.name if node.parent else ''),
        }
        
        # Create chunk with enhanced metadata
        chunk = {
            'id': f"{source_pdf}_{chunk_id}",
            'text': text,
            'source': source_pdf,
            'chunk_index': chunk_id,
            'length': len(text),
            'meta': meta,
            'hash': hashlib.md5(text.encode()).hexdigest()
        }
        
        chunks.append(chunk)
        chunk_id += 1
    
    return chunks


def extract_full_text_from_html(html_path: Path) -> str:
    """Extract full text content from HTML for semantic chunking"""
    soup = BeautifulSoup(html_path.read_text(), 'lxml')
    
    # Get all text content, preserving paragraph structure
    text_parts = []
    for node in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'div']):
        text = node.get_text(' ', strip=True)
        
        # Skip empty, very short, or page number texts
        if len(text) < 20 or text.startswith('Page ') or (text.isdigit() and len(text) < 4):
            continue
            
        text_parts.append(text)
    
    # Join with double newlines to preserve structure
    full_text = '\n\n'.join(text_parts)
    return full_text


def chunk_pdf_semantically(pdf_path: Path, source_pdf: str, chunker: SemanticTextChunker) -> list:
    """Create semantic chunks from PDF using max-min algorithm"""
    
    # Convert PDF to HTML
    html_path = pdf2html(pdf_path)
    
    # Extract full text
    full_text = extract_full_text_from_html(html_path)
    
    # Create semantic chunks
    semantic_chunks = chunker.chunk_text(full_text, source_pdf)
    
    # Clean up HTML file
    html_path.unlink()
    
    return semantic_chunks


def process_manual(pdf_path: Path, output_dir: Path, use_semantic: bool = False) -> None:
    """Process a single PDF manual to JSONL chunks"""
    print(f"Processing {pdf_path.name}...")
    
    if use_semantic:
        # Initialize semantic chunker (cached for reuse)
        if not hasattr(process_manual, '_chunker'):
            print("Initializing semantic text chunker...")
            process_manual._chunker = SemanticTextChunker(
                target_tokens=600,
                min_tokens=500, 
                max_tokens=700
            )
        
        # Create semantic chunks
        try:
            chunks = chunk_pdf_semantically(pdf_path, pdf_path.stem, process_manual._chunker)
            output_suffix = "_semantic_chunks.jsonl"
        except Exception as e:
            print(f"  Semantic chunking failed: {e}, falling back to DOM chunking")
            use_semantic = False
    
    if not use_semantic:
        # Convert PDF to HTML
        html_path = pdf2html(pdf_path)
        
        # Create chunks using DOM walking
        chunks = chunk_html_content(html_path, pdf_path.stem)
        output_suffix = "_dom_chunks.jsonl"
        
        # Clean up HTML file
        html_path.unlink()
    
    # Write to JSONL
    output_file = output_dir / f"{pdf_path.stem}{output_suffix}"
    with output_file.open('w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + '\n')
    
    # Create summary statistics
    if use_semantic:
        token_counts = [c.get("token_count", 0) for c in chunks]
        print(f"  Created {len(chunks)} semantic chunks -> {output_file}")
        if token_counts:
            print(f"  Token stats - Min: {min(token_counts)}, Max: {max(token_counts)}, Avg: {sum(token_counts)/len(token_counts):.1f}")
    else:
        tag_counts = {}
        hier_counts = {}
        for chunk in chunks:
            tag = chunk['meta']['tag']
            hier = chunk['meta']['hier']
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            hier_counts[hier] = hier_counts.get(hier, 0) + 1
        
        print(f"  Created {len(chunks)} DOM chunks -> {output_file}")
        print(f"  Tags: {dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))}")


def process_all_manuals(use_semantic: bool = True):
    """Process all PDF manuals in the manuals directory"""
    manuals_dir = Path("manuals")
    
    if use_semantic:
        processed_dir = Path("processed/semantic_chunks/docs")
        processed_dir.mkdir(parents=True, exist_ok=True)
        print("Using semantic chunking for PDF processing")
    else:
        processed_dir = Path("processed/docs")
        processed_dir.mkdir(parents=True, exist_ok=True)
        print("Using DOM-based chunking for PDF processing")
    
    pdf_files = list(manuals_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF manuals to process")
    
    for pdf_file in tqdm.tqdm(pdf_files, desc="Processing manuals"):
        try:
            process_manual(pdf_file, processed_dir, use_semantic=use_semantic)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")


if __name__ == "__main__":
    import sys
    use_semantic = True
    
    # Allow command line argument to disable semantic chunking
    if len(sys.argv) > 1 and sys.argv[1] == "--dom":
        use_semantic = False
    
    process_all_manuals(use_semantic=use_semantic)