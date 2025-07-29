#!/usr/bin/env python3
"""
Chunk Ingestion Pipeline for Vector Database

Loads semantic chunks from JSONL files, generates embeddings using appropriate models
based on content type, and ingests them into ChromaDB.
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Iterator, Tuple
from collections import defaultdict
import argparse

from vector_database import create_database


class ChunkIngester:
    """
    Pipeline for ingesting semantic chunks into the vector database.
    """
    
    def __init__(self, config_path: str = "vector_db_config.yaml"):
        """
        Initialize the chunk ingester.
        
        Args:
            config_path: Path to the configuration file
        """
        self.db = create_database(config_path)
        self.config = self.db.config
        self.logger = logging.getLogger(__name__)
        
        # Statistics tracking
        self.stats = {
            "start_time": None,
            "end_time": None,
            "files_processed": 0,
            "chunks_loaded": 0,
            "chunks_skipped": 0,
            "chunks_ingested": 0,
            "errors": [],
            "file_stats": [],
            "content_type_distribution": defaultdict(int),
            "duplicate_hashes": set()
        }
    
    def discover_chunk_files(self, source_dir: str) -> List[Path]:
        """
        Discover all semantic chunk JSONL files in the source directory.
        
        Args:
            source_dir: Directory containing semantic chunk files
            
        Returns:
            List of JSONL file paths
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        # Find all JSONL files
        jsonl_files = []
        for pattern in ["**/*_semantic_chunks.jsonl", "**/*.jsonl"]:
            jsonl_files.extend(source_path.glob(pattern))
        
        # Remove duplicates and sort
        jsonl_files = sorted(set(jsonl_files))
        
        self.logger.info(f"Discovered {len(jsonl_files)} JSONL files")
        return jsonl_files
    
    def load_chunks_from_file(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """
        Load chunks from a single JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Yields:
            Individual chunk dictionaries
        """
        self.logger.debug(f"Loading chunks from: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        chunk = json.loads(line)
                        yield chunk
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"JSON decode error in {file_path}:{line_num}: {e}"
                        self.logger.warning(error_msg)
                        self.stats["errors"].append(error_msg)
                        continue
                        
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {e}"
            self.logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    def determine_content_type(self, chunk: Dict[str, Any], file_path: Path) -> str:
        """
        Determine content type (document or code) for a chunk.
        
        Args:
            chunk: Chunk dictionary
            file_path: Source file path for context
            
        Returns:
            Content type string ('document' or 'code')
        """
        # Check if chunk already has content_type
        if 'content_type' in chunk:
            return chunk['content_type']
        
        # Infer from chunk structure and file path
        if 'source_path' in chunk or 'repo' in chunk or 'lang' in chunk:
            return 'code'
        elif 'source' in chunk and any(term in str(file_path).lower() 
                                     for term in ['doc', 'manual', 'pdf']):
            return 'document'
        elif '/docs/' in str(file_path):
            return 'document'
        elif '/code/' in str(file_path):
            return 'code'
        else:
            # Default fallback based on file path patterns
            if any(pattern in str(file_path) for pattern in ['_ast', 'mecademicpy', 'sample']):
                return 'code'
            else:
                return 'document'
    
    def validate_chunk(self, chunk: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a chunk for required fields and data quality.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['chunk_id', 'text']
        
        # Check required fields
        for field in required_fields:
            if field not in chunk:
                return False, f"Missing required field: {field}"
            
            if not chunk[field] or (isinstance(chunk[field], str) and not chunk[field].strip()):
                return False, f"Empty required field: {field}"
        
        # Check text content length
        text = chunk['text']
        if len(text) < 10:
            return False, f"Text too short: {len(text)} characters"
        
        if len(text) > 50000:  # Reasonable upper limit
            return False, f"Text too long: {len(text)} characters"
        
        return True, ""
    
    def compute_chunk_hash(self, chunk: Dict[str, Any]) -> str:
        """
        Compute hash for chunk deduplication.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Hash string
        """
        # Use existing hash if available
        if 'hash' in chunk:
            return chunk['hash']
        
        # Generate hash from chunk_id and text
        content = f"{chunk['chunk_id']}{chunk['text']}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_chunk(self, chunk: Dict[str, Any], file_path: Path) -> Tuple[bool, str]:
        """
        Process a single chunk: validate, deduplicate, and enrich.
        
        Args:
            chunk: Chunk dictionary
            file_path: Source file path
            
        Returns:
            Tuple of (should_include, skip_reason)
        """
        # Validate chunk
        is_valid, error_msg = self.validate_chunk(chunk)
        if not is_valid:
            return False, f"Validation failed: {error_msg}"
        
        # Compute hash for deduplication
        chunk_hash = self.compute_chunk_hash(chunk)
        if chunk_hash in self.stats["duplicate_hashes"]:
            return False, "Duplicate hash"
        
        self.stats["duplicate_hashes"].add(chunk_hash)
        
        # Determine and set content type
        content_type = self.determine_content_type(chunk, file_path)
        chunk['content_type'] = content_type
        
        # Update statistics
        self.stats["content_type_distribution"][content_type] += 1
        
        return True, ""
    
    def ingest_files(self, jsonl_files: List[Path], batch_size: int = 100) -> Dict[str, Any]:
        """
        Ingest chunks from multiple JSONL files.
        
        Args:
            jsonl_files: List of JSONL file paths
            batch_size: Number of chunks to process per batch
            
        Returns:
            Ingestion statistics
        """
        self.logger.info(f"Starting ingestion of {len(jsonl_files)} files...")
        self.stats["start_time"] = time.time()
        
        all_chunks = []
        
        # Load and process chunks from all files
        for file_path in jsonl_files:
            file_stats = {
                "file": str(file_path),
                "chunks_loaded": 0,
                "chunks_processed": 0,
                "chunks_skipped": 0,
                "errors": []
            }
            
            try:
                # Load chunks from file
                for chunk in self.load_chunks_from_file(file_path):
                    file_stats["chunks_loaded"] += 1
                    self.stats["chunks_loaded"] += 1
                    
                    # Process chunk
                    should_include, skip_reason = self.process_chunk(chunk, file_path)
                    
                    if should_include:
                        all_chunks.append(chunk)
                        file_stats["chunks_processed"] += 1
                    else:
                        file_stats["chunks_skipped"] += 1
                        self.stats["chunks_skipped"] += 1
                        self.logger.debug(f"Skipped chunk {chunk.get('chunk_id', 'unknown')}: {skip_reason}")
                
                self.stats["files_processed"] += 1
                self.stats["file_stats"].append(file_stats)
                
                self.logger.info(f"Processed {file_path.name}: {file_stats['chunks_processed']} chunks")
                
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {e}"
                self.logger.error(error_msg)
                self.stats["errors"].append(error_msg)
        
        # Ingest all chunks into database
        if all_chunks:
            self.logger.info(f"Ingesting {len(all_chunks)} chunks into database...")
            ingest_result = self.db.add_chunks(all_chunks, batch_size=batch_size)
            self.stats["chunks_ingested"] = ingest_result["chunks_processed"]
            self.stats["errors"].extend(ingest_result["errors"])
        
        self.stats["end_time"] = time.time()
        processing_time = self.stats["end_time"] - self.stats["start_time"]
        
        # Final statistics
        result = {
            "processing_time_seconds": processing_time,
            "files_processed": self.stats["files_processed"],
            "chunks_loaded": self.stats["chunks_loaded"],
            "chunks_skipped": self.stats["chunks_skipped"],
            "chunks_ingested": self.stats["chunks_ingested"],
            "content_type_distribution": dict(self.stats["content_type_distribution"]),
            "errors": self.stats["errors"],
            "success_rate": self.stats["chunks_ingested"] / self.stats["chunks_loaded"] if self.stats["chunks_loaded"] > 0 else 0
        }
        
        self.logger.info(f"Ingestion complete in {processing_time:.1f}s")
        self.logger.info(f"Loaded: {self.stats['chunks_loaded']}, Ingested: {self.stats['chunks_ingested']}, Skipped: {self.stats['chunks_skipped']}")
        self.logger.info(f"Content distribution: {dict(self.stats['content_type_distribution'])}")
        
        return result
    
    def ingest_from_directory(self, 
                             source_dir: str = None, 
                             batch_size: int = 100) -> Dict[str, Any]:
        """
        Main ingestion method: discover files and ingest chunks.
        
        Args:
            source_dir: Directory containing semantic chunk files
            batch_size: Number of chunks to process per batch
            
        Returns:
            Ingestion statistics
        """
        source_dir = source_dir or self.config["ingestion"]["source_directory"]
        
        # Discover files
        jsonl_files = self.discover_chunk_files(source_dir)
        
        if not jsonl_files:
            self.logger.warning(f"No JSONL files found in {source_dir}")
            return {"files_processed": 0, "chunks_ingested": 0, "errors": ["No files found"]}
        
        # Ingest files
        return self.ingest_files(jsonl_files, batch_size)
    
    def write_ingestion_report(self, stats: Dict[str, Any]) -> None:
        """
        Write detailed ingestion report.
        
        Args:
            stats: Ingestion statistics
        """
        # Create reports directory
        report_dir = Path(self.config['storage']['log_directory'])
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        json_report = report_dir / "ingestion_report.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, default=str)
        
        # Text summary
        text_report = report_dir / "ingestion_summary.txt"
        with open(text_report, 'w', encoding='utf-8') as f:
            f.write("Chunk Ingestion Report\n")
            f.write("=" * 30 + "\n\n")
            
            f.write(f"Processing Time: {stats['processing_time_seconds']:.1f} seconds\n")
            f.write(f"Files Processed: {stats['files_processed']}\n")
            f.write(f"Chunks Loaded: {stats['chunks_loaded']}\n")
            f.write(f"Chunks Ingested: {stats['chunks_ingested']}\n")
            f.write(f"Chunks Skipped: {stats['chunks_skipped']}\n")
            f.write(f"Success Rate: {stats['success_rate']:.2%}\n\n")
            
            f.write("Content Type Distribution:\n")
            for content_type, count in stats['content_type_distribution'].items():
                f.write(f"  {content_type}: {count}\n")
            
            if stats['errors']:
                f.write(f"\nErrors ({len(stats['errors'])}):\n")
                for error in stats['errors'][:10]:  # Limit to first 10 errors
                    f.write(f"  - {error}\n")
                if len(stats['errors']) > 10:
                    f.write(f"  ... and {len(stats['errors']) - 10} more errors\n")
        
        self.logger.info(f"Ingestion report written to: {report_dir}")


def main():
    """Main entry point for chunk ingestion."""
    parser = argparse.ArgumentParser(description="Ingest semantic chunks into vector database")
    parser.add_argument("--source-dir", help="Directory containing JSONL files")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
    parser.add_argument("--config", default="vector_db_config.yaml", help="Configuration file path")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    # Initialize ingester
    try:
        ingester = ChunkIngester(args.config)
        
        # Run ingestion
        stats = ingester.ingest_from_directory(
            source_dir=args.source_dir,
            batch_size=args.batch_size
        )
        
        # Generate report if requested
        if args.report:
            ingester.write_ingestion_report(stats)
        
        # Print summary
        print(f"\nIngestion Summary:")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Chunks ingested: {stats['chunks_ingested']}")
        print(f"Processing time: {stats['processing_time_seconds']:.1f}s")
        print(f"Success rate: {stats['success_rate']:.2%}")
        
        if stats['errors']:
            print(f"Errors: {len(stats['errors'])}")
            
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())