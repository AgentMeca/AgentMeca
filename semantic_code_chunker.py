#!/usr/bin/env python3
"""
Semantic Code Chunker for AST-based Code Chunks

Implements code chunking using AST boundaries with:
1. Processing existing AST extractions 
2. Comment/blank line stripping
3. SHA1-based hash generation for chunk IDs
4. Structured output with repo/commit/symbol metadata
"""

import json
import hashlib
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import subprocess

class SemanticCodeChunker:
    """
    Semantic code chunker that processes AST extractions into semantic chunks
    with hash-based IDs and enhanced metadata.
    """
    
    def __init__(self, repo_name: str = "meca_samples", commit_hash: Optional[str] = None):
        """
        Initialize the semantic code chunker.
        
        Args:
            repo_name: Name of the repository
            commit_hash: Git commit hash (auto-detected if None)
        """
        self.repo_name = repo_name
        self.commit_hash = commit_hash or self._get_git_commit()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Initialized code chunker for repo: {repo_name}, commit: {self.commit_hash}")
    
    def _get_git_commit(self) -> str:
        """
        Get the current git commit hash.
        
        Returns:
            Git commit hash (first 7 characters) or 'unknown'
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short=7', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.warning(f"Could not get git commit: {e}")
        
        return 'unknown'
    
    def strip_comments_and_blanks(self, code: str, language: str) -> str:
        """
        Strip comments and blank lines from code snippet.
        
        Args:
            code: Raw code snippet
            language: Programming language
            
        Returns:
            Cleaned code snippet
        """
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Language-specific comment removal
            if language in ['python']:
                # Skip single-line comments starting with #
                if stripped.startswith('#'):
                    continue
                # Remove inline comments (basic approach)
                if '#' in stripped and not stripped.startswith('"') and not stripped.startswith("'"):
                    # Simple heuristic - remove # and everything after if not in strings
                    parts = stripped.split('#')
                    if len(parts) > 1:
                        # Check if # is likely in a string (very basic check)
                        quote_count_single = parts[0].count("'")
                        quote_count_double = parts[0].count('"')
                        if quote_count_single % 2 == 0 and quote_count_double % 2 == 0:
                            stripped = parts[0].strip()
                            if not stripped:
                                continue
            
            elif language in ['javascript', 'c', 'csharp']:
                # Skip single-line comments starting with //
                if stripped.startswith('//'):
                    continue
                # Remove inline comments (basic approach)
                if '//' in stripped:
                    parts = stripped.split('//')
                    stripped = parts[0].strip()
                    if not stripped:
                        continue
                
                # Skip single-line /* */ comments
                if stripped.startswith('/*') and stripped.endswith('*/'):
                    continue
            
            cleaned_lines.append(line)  # Keep original indentation
        
        return '\n'.join(cleaned_lines)
    
    def compute_chunk_hash(self, code: str) -> str:
        """
        Compute SHA1 hash of code snippet.
        
        Args:
            code: Code snippet
            
        Returns:
            First 12 characters of SHA1 hash
        """
        return hashlib.sha1(code.encode('utf-8')).hexdigest()[:12]
    
    def extract_symbol_info(self, ast_node: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract symbol name and qualified name from AST node.
        
        Args:
            ast_node: AST node dictionary
            
        Returns:
            Tuple of (symbol_name, qualified_name)
        """
        symbol_name = ast_node.get('name')
        qualified_name = ast_node.get('qualified_name', symbol_name)
        
        # If no name, try to infer from chunk_type
        if not symbol_name:
            chunk_type = ast_node.get('chunk_type', '')
            node_type = ast_node.get('node_type', '')
            
            if chunk_type == 'import':
                # For imports, use the imported module/function name
                snippet = ast_node.get('snippet', '')
                if 'import' in snippet:
                    parts = snippet.split()
                    if 'from' in parts and 'import' in parts:
                        # from module import symbol
                        import_idx = parts.index('import')
                        if import_idx + 1 < len(parts):
                            symbol_name = parts[import_idx + 1].strip(',')
                    elif 'import' in parts:
                        # import module
                        import_idx = parts.index('import')
                        if import_idx + 1 < len(parts):
                            symbol_name = parts[import_idx + 1].strip(',')
            
            elif node_type:
                symbol_name = f"{node_type}_chunk"
        
        return symbol_name, qualified_name
    
    def normalize_file_path(self, file_path: str) -> str:
        """
        Normalize file path for consistent chunk IDs.
        
        Args:
            file_path: Original file path
            
        Returns:
            Normalized path relative to repo root
        """
        path = Path(file_path)
        
        # Try to make relative to known repo structures
        parts = path.parts
        
        # Look for common repo root indicators
        repo_indicators = ['repos', 'mecademicpy', 'sample-programs', 'meca500-accessories']
        
        for i, part in enumerate(parts):
            if part in repo_indicators:
                # Take everything after the repo indicator
                if i + 1 < len(parts):
                    relative_parts = parts[i + 1:]
                    return str(Path(*relative_parts))
        
        # If no repo structure found, use the last few path components
        if len(parts) > 3:
            return str(Path(*parts[-3:]))
        
        return str(path)
    
    def process_ast_node(self, ast_node: Dict, source_file: str) -> Dict:
        """
        Process a single AST node into a semantic code chunk.
        
        Args:
            ast_node: AST node from enhanced extraction
            source_file: Source file name for metadata
            
        Returns:
            Semantic code chunk dictionary
        """
        # Extract code snippet
        raw_snippet = ast_node.get('snippet', '')
        if not raw_snippet:
            return None
        
        # Get language
        language = ast_node.get('language', 'unknown')
        
        # Clean the code
        cleaned_snippet = self.strip_comments_and_blanks(raw_snippet, language)
        if not cleaned_snippet.strip():
            return None
        
        # Compute hash for chunk ID
        chunk_hash = self.compute_chunk_hash(cleaned_snippet)
        
        # Extract symbol information
        symbol_name, qualified_name = self.extract_symbol_info(ast_node)
        
        # Normalize source path
        normalized_path = self.normalize_file_path(ast_node.get('file_path', source_file))
        
        # Create chunk ID in the format: {repo}:{file}:{hash}
        chunk_id = f"{self.repo_name}:{normalized_path}:{chunk_hash}"
        
        # Get line location
        span = ast_node.get('span', [])
        start_line = span[0] if len(span) > 0 else None
        end_line = span[-1] if len(span) > 1 else start_line
        loc = [start_line, end_line] if start_line is not None else None
        
        # Create semantic chunk
        chunk = {
            "chunk_id": chunk_id,
            "repo": self.repo_name,
            "commit": self.commit_hash,
            "lang": language,
            "symbol": symbol_name,
            "qualified_name": qualified_name,
            "source_path": normalized_path,
            "loc": loc,
            "text": cleaned_snippet,
            "hash": chunk_hash,
            "chunk_type": ast_node.get('chunk_type'),
            "node_type": ast_node.get('node_type'),
            "signature": ast_node.get('signature'),
            "docstring": ast_node.get('docstring'),
            "chunk_size_bytes": len(cleaned_snippet),
            "original_size_bytes": ast_node.get('chunk_size_bytes', len(raw_snippet)),
            "start_byte": ast_node.get('start_byte'),
            "end_byte": ast_node.get('end_byte')
        }
        
        return chunk
    
    def process_ast_file(self, ast_file_path: Path) -> List[Dict]:
        """
        Process an AST extraction file into semantic code chunks.
        
        Args:
            ast_file_path: Path to AST JSON file
            
        Returns:
            List of semantic code chunks
        """
        self.logger.info(f"Processing AST file: {ast_file_path}")
        
        try:
            with open(ast_file_path, 'r', encoding='utf-8') as f:
                ast_nodes = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load AST file {ast_file_path}: {e}")
            return []
        
        if not isinstance(ast_nodes, list):
            self.logger.warning(f"Expected list of AST nodes in {ast_file_path}")
            return []
        
        chunks = []
        for ast_node in ast_nodes:
            chunk = self.process_ast_node(ast_node, str(ast_file_path))
            if chunk:
                chunks.append(chunk)
        
        self.logger.info(f"Generated {len(chunks)} chunks from {len(ast_nodes)} AST nodes")
        return chunks
    
    def process_directory(self, ast_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Process all AST files in a directory.
        
        Args:
            ast_dir: Directory containing AST JSON files
            output_dir: Directory to write semantic chunks
            
        Returns:
            Processing statistics
        """
        self.logger.info(f"Processing AST directory: {ast_dir}")
        
        # Find all AST JSON files
        ast_files = list(ast_dir.glob("**/*_ast.json")) + list(ast_dir.glob("**/*_enhanced_ast.json"))
        
        if not ast_files:
            self.logger.warning(f"No AST files found in {ast_dir}")
            return {"files_processed": 0, "chunks_created": 0}
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_chunks = 0
        chunk_stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "languages": {},
            "chunk_types": {},
            "size_stats": []
        }
        
        for ast_file in ast_files:
            chunks = self.process_ast_file(ast_file)
            
            if chunks:
                # Create output filename
                output_filename = ast_file.stem.replace("_ast", "").replace("_enhanced", "") + "_semantic_chunks.jsonl"
                output_path = output_dir / output_filename
                
                # Write chunks to JSONL
                with open(output_path, 'w', encoding='utf-8') as f:
                    for chunk in chunks:
                        f.write(json.dumps(chunk) + '\n')
                
                # Update statistics
                chunk_stats["files_processed"] += 1
                chunk_stats["chunks_created"] += len(chunks)
                
                for chunk in chunks:
                    lang = chunk.get("lang", "unknown")
                    chunk_type = chunk.get("chunk_type", "unknown")
                    size = chunk.get("chunk_size_bytes", 0)
                    
                    chunk_stats["languages"][lang] = chunk_stats["languages"].get(lang, 0) + 1
                    chunk_stats["chunk_types"][chunk_type] = chunk_stats["chunk_types"].get(chunk_type, 0) + 1
                    chunk_stats["size_stats"].append(size)
                
                self.logger.info(f"Wrote {len(chunks)} chunks to {output_path}")
        
        return chunk_stats


def main():
    """Example usage of SemanticCodeChunker"""
    
    # Initialize chunker
    chunker = SemanticCodeChunker(repo_name="meca_samples")
    
    # Example: Process the enhanced AST extractions
    ast_dir = Path("/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/processed/code_enhanced")
    output_dir = Path("/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/processed/semantic_chunks/code")
    
    if ast_dir.exists():
        stats = chunker.process_directory(ast_dir, output_dir)
        print(f"\nProcessing Statistics:")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Chunks created: {stats['chunks_created']}")
        print(f"Languages: {dict(stats['languages'])}")
        print(f"Chunk types: {dict(stats['chunk_types'])}")
        
        if stats['size_stats']:
            import numpy as np
            sizes = np.array(stats['size_stats'])
            print(f"Size stats (bytes) - Min: {np.min(sizes)}, Max: {np.max(sizes)}, Mean: {np.mean(sizes):.1f}")
    else:
        print(f"AST directory not found: {ast_dir}")


if __name__ == "__main__":
    main()