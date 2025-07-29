#!/usr/bin/env python3
"""
Unified Semantic Processing Pipeline

Main script that orchestrates semantic chunking for both text documents and code files.
Provides progress tracking, statistics, and quality reporting.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from semantic_text_chunker import SemanticTextChunker
from semantic_code_chunker import SemanticCodeChunker
from pdf_processor import process_manual

class SemanticProcessingPipeline:
    """
    Unified pipeline for semantic processing of documents and code.
    """
    
    def __init__(self, output_base_dir: str = "processed/semantic_chunks"):
        """
        Initialize the semantic processing pipeline.
        
        Args:
            output_base_dir: Base directory for all semantic chunk outputs
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize output directories
        self.docs_output_dir = self.output_base_dir / "docs" 
        self.code_output_dir = self.output_base_dir / "code"
        self.docs_output_dir.mkdir(parents=True, exist_ok=True)
        self.code_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize chunkers (lazy loading)
        self._text_chunker = None
        self._code_chunker = None
        
        # Statistics tracking
        self.stats = {
            "start_time": None,
            "end_time": None,
            "docs_processed": 0,
            "code_files_processed": 0,
            "total_text_chunks": 0,
            "total_code_chunks": 0,
            "text_chunk_stats": [],
            "code_chunk_stats": [],
            "errors": []
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    @property
    def text_chunker(self) -> SemanticTextChunker:
        """Lazy-load text chunker to avoid loading model unnecessarily."""
        if self._text_chunker is None:
            self.logger.info("Initializing semantic text chunker...")
            self._text_chunker = SemanticTextChunker(
                target_tokens=600,
                min_tokens=500,
                max_tokens=700
            )
        return self._text_chunker
    
    @property
    def code_chunker(self) -> SemanticCodeChunker:
        """Lazy-load code chunker."""
        if self._code_chunker is None:
            self.logger.info("Initializing semantic code chunker...")
            self._code_chunker = SemanticCodeChunker(repo_name="meca_samples")
        return self._code_chunker
    
    def process_documents(self, manuals_dir: str = "manuals") -> Dict[str, Any]:
        """
        Process all PDF documents using semantic chunking.
        
        Args:
            manuals_dir: Directory containing PDF manuals
            
        Returns:
            Processing statistics for documents
        """
        self.logger.info("Starting document processing...")
        
        manuals_path = Path(manuals_dir)
        if not manuals_path.exists():
            self.logger.warning(f"Manuals directory not found: {manuals_path}")
            return {"processed": 0, "chunks": 0, "errors": []}
        
        pdf_files = list(manuals_path.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        doc_stats = {
            "processed": 0,
            "chunks": 0,
            "errors": [],
            "files": []
        }
        
        for pdf_file in pdf_files:
            try:
                self.logger.info(f"Processing document: {pdf_file.name}")
                
                # Use the process_manual function with semantic chunking
                process_manual(pdf_file, self.docs_output_dir, use_semantic=True)
                
                # Count chunks in output file
                output_file = self.docs_output_dir / f"{pdf_file.stem}_semantic_chunks.jsonl"
                if output_file.exists():
                    chunk_count = sum(1 for _ in open(output_file))
                    doc_stats["chunks"] += chunk_count
                    doc_stats["files"].append({
                        "file": pdf_file.name,
                        "chunks": chunk_count
                    })
                
                doc_stats["processed"] += 1
                self.stats["docs_processed"] += 1
                
            except Exception as e:
                error_msg = f"Error processing {pdf_file.name}: {str(e)}"
                self.logger.error(error_msg)
                doc_stats["errors"].append(error_msg)
                self.stats["errors"].append(error_msg)
        
        self.stats["total_text_chunks"] += doc_stats["chunks"]
        self.logger.info(f"Document processing complete: {doc_stats['processed']} files, {doc_stats['chunks']} chunks")
        return doc_stats
    
    def process_code(self, ast_dir: str = "processed/code_enhanced") -> Dict[str, Any]:
        """
        Process all code files using semantic chunking.
        
        Args:
            ast_dir: Directory containing enhanced AST extractions
            
        Returns:
            Processing statistics for code
        """
        self.logger.info("Starting code processing...")
        
        ast_path = Path(ast_dir)
        if not ast_path.exists():
            self.logger.warning(f"AST directory not found: {ast_path}")
            return {"processed": 0, "chunks": 0, "errors": []}
        
        # Process code using the code chunker
        code_stats = self.code_chunker.process_directory(ast_path, self.code_output_dir)
        
        self.stats["code_files_processed"] = code_stats["files_processed"]
        self.stats["total_code_chunks"] = code_stats["chunks_created"]
        
        self.logger.info(f"Code processing complete: {code_stats['files_processed']} files, {code_stats['chunks_created']} chunks")
        return code_stats
    
    def process_all(self, 
                   manuals_dir: str = "manuals",
                   ast_dir: str = "processed/code_enhanced") -> Dict[str, Any]:
        """
        Process both documents and code using semantic chunking.
        
        Args:
            manuals_dir: Directory containing PDF manuals
            ast_dir: Directory containing enhanced AST extractions
            
        Returns:
            Complete processing statistics
        """
        self.logger.info("Starting complete semantic processing pipeline...")
        self.stats["start_time"] = time.time()
        
        # Process documents
        doc_stats = self.process_documents(manuals_dir)
        
        # Process code
        code_stats = self.process_code(ast_dir)
        
        self.stats["end_time"] = time.time()
        processing_time = self.stats["end_time"] - self.stats["start_time"]
        
        # Combine statistics
        combined_stats = {
            "processing_time_seconds": processing_time,
            "documents": doc_stats,
            "code": code_stats,
            "totals": {
                "files_processed": self.stats["docs_processed"] + self.stats["code_files_processed"],
                "chunks_created": self.stats["total_text_chunks"] + self.stats["total_code_chunks"],
                "text_chunks": self.stats["total_text_chunks"],
                "code_chunks": self.stats["total_code_chunks"]
            },
            "errors": self.stats["errors"]
        }
        
        # Write processing report
        self.write_processing_report(combined_stats)
        
        self.logger.info(f"Pipeline complete in {processing_time:.1f}s")
        self.logger.info(f"Total: {combined_stats['totals']['files_processed']} files, {combined_stats['totals']['chunks_created']} chunks")
        
        return combined_stats
    
    def write_processing_report(self, stats: Dict[str, Any]) -> None:
        """
        Write a detailed processing report.
        
        Args:
            stats: Processing statistics
        """
        report_file = self.output_base_dir / "processing_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        
        self.logger.info(f"Processing report written to: {report_file}")
        
        # Also write a human-readable summary
        summary_file = self.output_base_dir / "processing_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Semantic Processing Pipeline Summary\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Processing Time: {stats['processing_time_seconds']:.1f} seconds\n\n")
            
            f.write("Documents:\n")
            f.write(f"  Files processed: {stats['documents']['processed']}\n")
            f.write(f"  Chunks created: {stats['documents']['chunks']}\n")
            f.write(f"  Errors: {len(stats['documents']['errors'])}\n\n")
            
            f.write("Code:\n")
            f.write(f"  Files processed: {stats['code']['files_processed']}\n")
            f.write(f"  Chunks created: {stats['code']['chunks_created']}\n")
            
            if 'languages' in stats['code']:
                f.write(f"  Languages: {dict(stats['code']['languages'])}\n")
            if 'chunk_types' in stats['code']:
                f.write(f"  Chunk types: {dict(stats['code']['chunk_types'])}\n")
            
            if 'size_stats' in stats['code'] and stats['code']['size_stats']:
                sizes = np.array(stats['code']['size_stats'])
                f.write(f"  Size stats (bytes): Min={np.min(sizes)}, Max={np.max(sizes)}, Mean={np.mean(sizes):.1f}\n")
            
            f.write(f"\nTotals:\n")
            f.write(f"  Total files: {stats['totals']['files_processed']}\n")
            f.write(f"  Total chunks: {stats['totals']['chunks_created']}\n")
            f.write(f"  Text chunks: {stats['totals']['text_chunks']}\n")
            f.write(f"  Code chunks: {stats['totals']['code_chunks']}\n")
            
            if stats['errors']:
                f.write(f"\nErrors ({len(stats['errors'])}):\n")
                for error in stats['errors']:
                    f.write(f"  - {error}\n")
        
        self.logger.info(f"Processing summary written to: {summary_file}")
    
    def validate_output(self) -> Dict[str, Any]:
        """
        Validate the output chunks and compute quality metrics.
        
        Returns:
            Validation results and quality metrics
        """
        self.logger.info("Validating output chunks...")
        
        validation_results = {
            "docs": {"files": 0, "chunks": 0, "avg_tokens": 0, "token_range": [0, 0]},
            "code": {"files": 0, "chunks": 0, "avg_size": 0, "size_range": [0, 0]},
            "issues": []
        }
        
        # Validate document chunks
        doc_files = list(self.docs_output_dir.glob("*.jsonl"))
        validation_results["docs"]["files"] = len(doc_files)
        
        doc_token_counts = []
        for doc_file in doc_files:
            with open(doc_file, 'r') as f:
                for line in f:
                    chunk = json.loads(line)
                    token_count = chunk.get("token_count", 0)
                    doc_token_counts.append(token_count)
        
        if doc_token_counts:
            validation_results["docs"]["chunks"] = len(doc_token_counts)
            validation_results["docs"]["avg_tokens"] = np.mean(doc_token_counts)
            validation_results["docs"]["token_range"] = [min(doc_token_counts), max(doc_token_counts)]
        
        # Validate code chunks
        code_files = list(self.code_output_dir.glob("*.jsonl"))
        validation_results["code"]["files"] = len(code_files)
        
        code_sizes = []
        for code_file in code_files:
            with open(code_file, 'r') as f:
                for line in f:
                    chunk = json.loads(line)
                    size = chunk.get("chunk_size_bytes", 0)
                    code_sizes.append(size)
        
        if code_sizes:
            validation_results["code"]["chunks"] = len(code_sizes)
            validation_results["code"]["avg_size"] = np.mean(code_sizes)
            validation_results["code"]["size_range"] = [min(code_sizes), max(code_sizes)]
        
        self.logger.info(f"Validation complete: {validation_results['docs']['chunks']} doc chunks, {validation_results['code']['chunks']} code chunks")
        return validation_results


def main():
    """Main entry point for semantic processing pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic Processing Pipeline for Documents and Code")
    parser.add_argument("--docs-only", action="store_true", help="Process only documents")
    parser.add_argument("--code-only", action="store_true", help="Process only code")
    parser.add_argument("--manuals-dir", default="manuals", help="Directory containing PDF manuals")
    parser.add_argument("--ast-dir", default="processed/code_enhanced", help="Directory containing AST files")
    parser.add_argument("--output-dir", default="processed/semantic_chunks", help="Output directory for chunks")
    parser.add_argument("--validate", action="store_true", help="Run validation after processing")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = SemanticProcessingPipeline(args.output_dir)
    
    # Process based on arguments
    if args.docs_only:
        stats = {"documents": pipeline.process_documents(args.manuals_dir)}
    elif args.code_only:
        stats = {"code": pipeline.process_code(args.ast_dir)}
    else:
        stats = pipeline.process_all(args.manuals_dir, args.ast_dir)
    
    # Run validation if requested
    if args.validate:
        validation = pipeline.validate_output()
        print("\nValidation Results:")
        print(f"Document chunks: {validation['docs']['chunks']} (avg {validation['docs']['avg_tokens']:.1f} tokens)")
        print(f"Code chunks: {validation['code']['chunks']} (avg {validation['code']['avg_size']:.1f} bytes)")
    
    print("\nProcessing complete! Check the output directory for results.")


if __name__ == "__main__":
    main()