#!/usr/bin/env python3
"""
Chunk Quality Validator

Implements quality metrics and validation testing for semantic chunk coherence.
Compares semantic chunking against baseline approaches and provides detailed analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
from collections import defaultdict, Counter

# Import semantic chunker for comparison
from semantic_text_chunker import SemanticTextChunker

class ChunkQualityValidator:
    """
    Validator for chunk quality metrics and coherence analysis.
    """
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_chunks_from_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load chunks from a JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return chunks
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    chunk = json.loads(line.strip())
                    chunks.append(chunk)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON in {file_path}: {e}")
        
        return chunks
    
    def validate_document_chunks(self, chunks_dir: Path) -> Dict[str, Any]:
        """
        Validate document chunks for quality metrics.
        
        Args:
            chunks_dir: Directory containing document chunk files
            
        Returns:
            Validation results for document chunks
        """
        self.logger.info("Validating document chunks...")
        
        chunk_files = list(chunks_dir.glob("*_semantic_chunks.jsonl"))
        
        validation_results = {
            "total_files": len(chunk_files),
            "total_chunks": 0,
            "token_statistics": {},
            "chunk_coherence": {},
            "file_details": [],
            "quality_issues": []
        }
        
        all_token_counts = []
        all_sentence_counts = []
        all_char_counts = []
        
        for chunk_file in chunk_files:
            self.logger.info(f"Validating {chunk_file.name}...")
            
            chunks = self.load_chunks_from_jsonl(chunk_file)
            if not chunks:
                continue
            
            file_details = {
                "file": chunk_file.name,
                "chunks": len(chunks),
                "token_range": [float('inf'), 0],
                "avg_tokens": 0,
                "issues": []
            }
            
            file_token_counts = []
            file_sentence_counts = []
            file_char_counts = []
            
            for i, chunk in enumerate(chunks):
                # Extract metrics
                token_count = chunk.get("token_count", 0)
                sentence_count = chunk.get("sentence_count", 0) 
                char_count = chunk.get("char_count", 0)
                
                file_token_counts.append(token_count)
                file_sentence_counts.append(sentence_count)
                file_char_counts.append(char_count)
                
                all_token_counts.append(token_count)
                all_sentence_counts.append(sentence_count)
                all_char_counts.append(char_count)
                
                # Check for quality issues
                if token_count < 300:
                    file_details["issues"].append(f"Chunk {i}: Low token count ({token_count})")
                elif token_count > 800:
                    file_details["issues"].append(f"Chunk {i}: High token count ({token_count})")
                
                if sentence_count < 2:
                    file_details["issues"].append(f"Chunk {i}: Too few sentences ({sentence_count})")
                
                if len(chunk.get("text", "")) < 100:
                    file_details["issues"].append(f"Chunk {i}: Very short text")
            
            # Calculate file statistics
            if file_token_counts:
                file_details["token_range"] = [min(file_token_counts), max(file_token_counts)]
                file_details["avg_tokens"] = np.mean(file_token_counts)
            
            validation_results["file_details"].append(file_details)
            validation_results["total_chunks"] += len(chunks)
        
        # Calculate overall statistics
        if all_token_counts:
            validation_results["token_statistics"] = {
                "count": len(all_token_counts),
                "mean": np.mean(all_token_counts),
                "median": np.median(all_token_counts),
                "std": np.std(all_token_counts),
                "min": min(all_token_counts),
                "max": max(all_token_counts),
                "target_range_compliance": sum(1 for t in all_token_counts if 500 <= t <= 700) / len(all_token_counts)
            }
        
        if all_sentence_counts:
            validation_results["sentence_statistics"] = {
                "mean": np.mean(all_sentence_counts),
                "median": np.median(all_sentence_counts),
                "min": min(all_sentence_counts),
                "max": max(all_sentence_counts)
            }
        
        self.logger.info(f"Document validation complete: {validation_results['total_chunks']} chunks across {validation_results['total_files']} files")
        return validation_results
    
    def validate_code_chunks(self, chunks_dir: Path) -> Dict[str, Any]:
        """
        Validate code chunks for quality metrics.
        
        Args:
            chunks_dir: Directory containing code chunk files
            
        Returns:
            Validation results for code chunks
        """
        self.logger.info("Validating code chunks...")
        
        chunk_files = list(chunks_dir.glob("*_semantic_chunks.jsonl"))
        
        validation_results = {
            "total_files": len(chunk_files),
            "total_chunks": 0,
            "size_statistics": {},
            "language_distribution": {},
            "chunk_type_distribution": {},
            "hash_uniqueness": {},
            "quality_issues": []
        }
        
        all_sizes = []
        all_hashes = []
        language_counts = Counter()
        chunk_type_counts = Counter()
        
        for chunk_file in chunk_files:
            chunks = self.load_chunks_from_jsonl(chunk_file)
            if not chunks:
                continue
            
            for chunk in chunks:
                # Size statistics
                size = chunk.get("chunk_size_bytes", 0)
                all_sizes.append(size)
                
                # Hash uniqueness
                chunk_hash = chunk.get("hash", "")
                if chunk_hash:
                    all_hashes.append(chunk_hash)
                
                # Language and type distribution
                language = chunk.get("lang", "unknown")
                chunk_type = chunk.get("chunk_type", "unknown")
                
                language_counts[language] += 1
                chunk_type_counts[chunk_type] += 1
                
                # Quality checks
                if size < 10:
                    validation_results["quality_issues"].append(f"Very small chunk: {chunk.get('chunk_id', 'unknown')}")
                
                if not chunk.get("symbol"):
                    validation_results["quality_issues"].append(f"Missing symbol: {chunk.get('chunk_id', 'unknown')}")
            
            validation_results["total_chunks"] += len(chunks)
        
        # Calculate statistics
        if all_sizes:
            validation_results["size_statistics"] = {
                "count": len(all_sizes),
                "mean": np.mean(all_sizes),
                "median": np.median(all_sizes),
                "std": np.std(all_sizes),
                "min": min(all_sizes),
                "max": max(all_sizes)
            }
        
        validation_results["language_distribution"] = dict(language_counts)
        validation_results["chunk_type_distribution"] = dict(chunk_type_counts)
        
        # Hash uniqueness check
        if all_hashes:
            unique_hashes = len(set(all_hashes))
            total_hashes = len(all_hashes)
            validation_results["hash_uniqueness"] = {
                "total_hashes": total_hashes,
                "unique_hashes": unique_hashes,
                "uniqueness_ratio": unique_hashes / total_hashes,
                "duplicates": total_hashes - unique_hashes
            }
        
        self.logger.info(f"Code validation complete: {validation_results['total_chunks']} chunks across {validation_results['total_files']} files")
        return validation_results
    
    def compare_chunking_approaches(self, 
                                  semantic_chunks_dir: Path,
                                  baseline_chunks_dir: Path) -> Dict[str, Any]:
        """
        Compare semantic chunking against baseline (DOM) chunking.
        
        Args:
            semantic_chunks_dir: Directory with semantic chunks
            baseline_chunks_dir: Directory with baseline chunks
            
        Returns:
            Comparison results
        """
        self.logger.info("Comparing semantic vs baseline chunking...")
        
        comparison_results = {
            "semantic": {"total_chunks": 0, "avg_size": 0, "files": 0},
            "baseline": {"total_chunks": 0, "avg_size": 0, "files": 0},
            "improvement_metrics": {}
        }
        
        # Analyze semantic chunks
        semantic_files = list(semantic_chunks_dir.glob("*_semantic_chunks.jsonl"))
        semantic_token_counts = []
        
        for file_path in semantic_files:
            chunks = self.load_chunks_from_jsonl(file_path)
            comparison_results["semantic"]["total_chunks"] += len(chunks)
            
            for chunk in chunks:
                token_count = chunk.get("token_count", chunk.get("length", 0))
                semantic_token_counts.append(token_count)
        
        comparison_results["semantic"]["files"] = len(semantic_files)
        if semantic_token_counts:
            comparison_results["semantic"]["avg_size"] = np.mean(semantic_token_counts)
            comparison_results["semantic"]["size_std"] = np.std(semantic_token_counts)
        
        # Analyze baseline chunks
        baseline_files = list(baseline_chunks_dir.glob("*_dom_chunks.jsonl"))
        baseline_sizes = []
        
        for file_path in baseline_files:
            chunks = self.load_chunks_from_jsonl(file_path)
            comparison_results["baseline"]["total_chunks"] += len(chunks)
            
            for chunk in chunks:
                size = chunk.get("length", len(chunk.get("text", "")))
                baseline_sizes.append(size)
        
        comparison_results["baseline"]["files"] = len(baseline_files)
        if baseline_sizes:
            comparison_results["baseline"]["avg_size"] = np.mean(baseline_sizes)
            comparison_results["baseline"]["size_std"] = np.std(baseline_sizes)
        
        # Calculate improvement metrics
        if semantic_token_counts and baseline_sizes:
            # Size consistency (lower std is better)
            semantic_cv = np.std(semantic_token_counts) / np.mean(semantic_token_counts)
            baseline_cv = np.std(baseline_sizes) / np.mean(baseline_sizes)
            
            comparison_results["improvement_metrics"] = {
                "size_consistency_improvement": (baseline_cv - semantic_cv) / baseline_cv,
                "semantic_cv": semantic_cv,
                "baseline_cv": baseline_cv,
                "chunk_reduction_ratio": comparison_results["baseline"]["total_chunks"] / comparison_results["semantic"]["total_chunks"] if comparison_results["semantic"]["total_chunks"] > 0 else 0
            }
        
        return comparison_results
    
    def generate_quality_report(self, 
                              semantic_chunks_dir: Path,
                              baseline_chunks_dir: Path = None) -> Dict[str, Any]:
        """
        Generate comprehensive quality report.
        
        Args:
            semantic_chunks_dir: Directory with semantic chunks
            baseline_chunks_dir: Optional directory with baseline chunks for comparison
            
        Returns:
            Complete quality report
        """
        self.logger.info("Generating comprehensive quality report...")
        
        report = {
            "timestamp": str(np.datetime64('now')),
            "semantic_chunks_validation": {},
            "code_chunks_validation": {},
            "comparison_results": None,
            "summary": {},
            "recommendations": []
        }
        
        # Validate document chunks
        docs_dir = semantic_chunks_dir / "docs" if (semantic_chunks_dir / "docs").exists() else semantic_chunks_dir
        if docs_dir.exists():
            report["semantic_chunks_validation"] = self.validate_document_chunks(docs_dir)
        
        # Validate code chunks
        code_dir = semantic_chunks_dir / "code" if (semantic_chunks_dir / "code").exists() else semantic_chunks_dir
        if code_dir.exists():
            report["code_chunks_validation"] = self.validate_code_chunks(code_dir)
        
        # Compare with baseline if available
        if baseline_chunks_dir and baseline_chunks_dir.exists():
            report["comparison_results"] = self.compare_chunking_approaches(
                semantic_chunks_dir, baseline_chunks_dir
            )
        
        # Generate summary
        total_chunks = 0
        total_files = 0
        
        if "semantic_chunks_validation" in report:
            total_chunks += report["semantic_chunks_validation"].get("total_chunks", 0)
            total_files += report["semantic_chunks_validation"].get("total_files", 0)
        
        if "code_chunks_validation" in report:
            total_chunks += report["code_chunks_validation"].get("total_chunks", 0)
            total_files += report["code_chunks_validation"].get("total_files", 0)
        
        report["summary"] = {
            "total_chunks_validated": total_chunks,
            "total_files_validated": total_files,
            "overall_quality": "Good" if total_chunks > 0 else "No data"
        }
        
        # Generate recommendations
        recommendations = []
        
        if "semantic_chunks_validation" in report:
            doc_stats = report["semantic_chunks_validation"].get("token_statistics", {})
            compliance = doc_stats.get("target_range_compliance", 0)
            
            if compliance < 0.8:
                recommendations.append("Consider adjusting token range parameters for better compliance")
            
            if doc_stats.get("std", 0) > 100:
                recommendations.append("High token count variance detected - review chunking algorithm")
        
        if "code_chunks_validation" in report:
            code_issues = len(report["code_chunks_validation"].get("quality_issues", []))
            if code_issues > 0:
                recommendations.append(f"Address {code_issues} code chunk quality issues")
        
        if not recommendations:
            recommendations.append("Chunking quality looks good - no major issues detected")
        
        report["recommendations"] = recommendations
        
        return report
    
    def write_quality_report(self, report: Dict[str, Any], output_file: Path) -> None:
        """
        Write quality report to file.
        
        Args:
            report: Quality report dictionary
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Also write human-readable summary
        summary_file = output_file.with_suffix('.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Semantic Chunking Quality Report\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Generated: {report['timestamp']}\n\n")
            
            # Summary
            summary = report.get("summary", {})
            f.write(f"Total chunks validated: {summary.get('total_chunks_validated', 0)}\n")
            f.write(f"Total files validated: {summary.get('total_files_validated', 0)}\n")
            f.write(f"Overall quality: {summary.get('overall_quality', 'Unknown')}\n\n")
            
            # Document chunk details
            if "semantic_chunks_validation" in report:
                doc_val = report["semantic_chunks_validation"]
                token_stats = doc_val.get("token_statistics", {})
                
                f.write("Document Chunks:\n")
                f.write(f"  Files: {doc_val.get('total_files', 0)}\n")
                f.write(f"  Chunks: {doc_val.get('total_chunks', 0)}\n")
                
                if token_stats:
                    f.write(f"  Token range compliance: {token_stats.get('target_range_compliance', 0):.2%}\n")
                    f.write(f"  Mean tokens: {token_stats.get('mean', 0):.1f}\n")
                    f.write(f"  Token range: {token_stats.get('min', 0)}-{token_stats.get('max', 0)}\n")
                
                f.write("\n")
            
            # Code chunk details
            if "code_chunks_validation" in report:
                code_val = report["code_chunks_validation"]
                size_stats = code_val.get("size_statistics", {})
                
                f.write("Code Chunks:\n")
                f.write(f"  Files: {code_val.get('total_files', 0)}\n")
                f.write(f"  Chunks: {code_val.get('total_chunks', 0)}\n")
                
                if size_stats:
                    f.write(f"  Mean size: {size_stats.get('mean', 0):.1f} bytes\n")
                    f.write(f"  Size range: {size_stats.get('min', 0)}-{size_stats.get('max', 0)}\n")
                
                # Language distribution
                lang_dist = code_val.get("language_distribution", {})
                if lang_dist:
                    f.write(f"  Languages: {dict(lang_dist)}\n")
                
                f.write("\n")
            
            # Recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                f.write("Recommendations:\n")
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"  {i}. {rec}\n")
        
        self.logger.info(f"Quality report written to: {output_file}")
        self.logger.info(f"Summary written to: {summary_file}")


def main():
    """Main entry point for quality validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Semantic Chunk Quality")
    parser.add_argument("--semantic-dir", default="processed/semantic_chunks", 
                       help="Directory containing semantic chunks")
    parser.add_argument("--baseline-dir", default="processed/docs",
                       help="Directory containing baseline chunks for comparison")
    parser.add_argument("--output-file", default="chunk_quality_report.json",
                       help="Output file for quality report")
    parser.add_argument("--no-comparison", action="store_true",
                       help="Skip comparison with baseline chunks")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ChunkQualityValidator()
    
    # Generate quality report
    semantic_dir = Path(args.semantic_dir)
    baseline_dir = Path(args.baseline_dir) if not args.no_comparison else None
    
    report = validator.generate_quality_report(semantic_dir, baseline_dir)
    
    # Write report
    output_file = Path(args.output_file)
    validator.write_quality_report(report, output_file)
    
    # Print summary
    print("\nQuality Validation Summary:")
    print(f"Total chunks: {report['summary']['total_chunks_validated']}")
    print(f"Total files: {report['summary']['total_files_validated']}")
    print(f"Overall quality: {report['summary']['overall_quality']}")
    
    if report["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()