from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import tqdm
import re


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


def process_manual(pdf_path: Path, output_dir: Path) -> None:
    """Process a single PDF manual to JSONL chunks"""
    print(f"Processing {pdf_path.name}...")
    
    # Convert PDF to HTML
    html_path = pdf2html(pdf_path)
    
    # Create chunks using DOM walking
    chunks = chunk_html_content(html_path, pdf_path.stem)
    
    # Write to JSONL
    output_file = output_dir / f"{pdf_path.stem}_dom_chunks.jsonl"
    with output_file.open('w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + '\n')
    
    # Create summary of metadata
    tag_counts = {}
    hier_counts = {}
    for chunk in chunks:
        tag = chunk['meta']['tag']
        hier = chunk['meta']['hier']
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        hier_counts[hier] = hier_counts.get(hier, 0) + 1
    
    print(f"  Created {len(chunks)} chunks -> {output_file}")
    print(f"  Tags: {dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))}")
    
    # Clean up HTML file
    html_path.unlink()


def process_all_manuals():
    """Process all PDF manuals in the manuals directory"""
    manuals_dir = Path("manuals")
    processed_dir = Path("processed/docs")
    
    pdf_files = list(manuals_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF manuals to process")
    
    for pdf_file in tqdm.tqdm(pdf_files, desc="Processing manuals"):
        try:
            process_manual(pdf_file, processed_dir)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")


if __name__ == "__main__":
    process_all_manuals()