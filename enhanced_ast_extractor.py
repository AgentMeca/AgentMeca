#!/usr/bin/env python3
"""
Enhanced AST Extractor for Code Files using Tree-sitter
Provides method-level granularity and optimized chunk sizes for better embedding and retrieval.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
from tree_sitter import Parser
from tree_sitter_language_pack import get_language

class EnhancedASTExtractor:
    """Extract fine-grained AST units from source code files using Tree-sitter."""
    
    # Target chunk size for optimal embedding performance
    TARGET_CHUNK_SIZE = 2048  # 2KB target, allows 1-3KB range
    MAX_CHUNK_SIZE = 4096     # 4KB maximum before forced splitting
    
    # Language-specific node types for different granularities
    TOP_LEVEL_NODES = {
        'python': [
            'function_definition',
            'class_definition', 
            'import_statement',
            'import_from_statement',
            'assignment'  # for module-level constants
        ],
        'javascript': [
            'function_declaration',
            'class_declaration',
            'export_statement',
            'import_statement',
            'variable_declaration',
            'expression_statement'
        ],
        'c': [
            'function_definition',
            'struct_specifier',
            'declaration',
            'preproc_include'
        ],
        'csharp': [
            'class_declaration',
            'interface_declaration',
            'method_declaration',
            'namespace_declaration',
            'using_directive'
        ]
    }
    
    # Method/function node types for nested extraction
    METHOD_NODES = {
        'python': ['function_definition'],
        'javascript': ['function_declaration', 'method_definition'],
        'c': ['function_definition'],
        'csharp': ['method_declaration', 'constructor_declaration']
    }
    
    # File extensions to language mapping
    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp'
    }
    
    def __init__(self):
        """Initialize the enhanced AST extractor with language parsers."""
        self.parsers = {}
        self.setup_logging()
        self.setup_parsers()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        for lang in self.TOP_LEVEL_NODES:
            try:
                ts_lang = get_language(lang)
                
                # Try the new zero-arg Parser + set_language() API
                try:
                    parser = Parser()
                    parser.set_language(ts_lang)
                except (AttributeError, TypeError):
                    # Fallback: old-style constructor took the Language as argument
                    parser = Parser(ts_lang)

                self.parsers[lang] = parser
                self.logger.info(f"Loaded {lang} parser")
            except Exception as e:
                self.logger.error(f"Failed to load {lang} parser: {e}")
    
    def get_language_from_file(self, file_path: str) -> Optional[str]:
        """Determine the programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_EXTENSIONS.get(ext)
    
    def normalize_file_path(self, file_path: str, relative_to: str) -> str:
        """Normalize file path by removing Windows-style paths and spaces."""
        rel_path = os.path.relpath(file_path, relative_to)
        # Convert to forward slashes and remove any problematic characters
        normalized = rel_path.replace('\\', '/').replace(' ', '_')
        return normalized
    
    def extract_docstring(self, node, code: str, language: str) -> Optional[str]:
        """Extract docstring from function/class definition."""
        if language != 'python':
            return None
            
        # For Python, look for string literal as first statement in body
        if hasattr(node, 'child_by_field_name'):
            body = node.child_by_field_name('body')
            if body and body.children:
                first_stmt = body.children[0]
                if first_stmt.type == 'expression_statement':
                    expr = first_stmt.children[0] if first_stmt.children else None
                    if expr and expr.type == 'string':
                        docstring = code[expr.start_byte:expr.end_byte]
                        # Clean up the docstring (remove quotes, normalize whitespace)
                        return docstring.strip('"\'').strip()
        return None
    
    def extract_function_signature(self, node, code: str, language: str) -> str:
        """Extract function signature (name + parameters) from function node."""
        try:
            if language == 'python':
                name_node = node.child_by_field_name('name')
                params_node = node.child_by_field_name('parameters')
                
                name = code[name_node.start_byte:name_node.end_byte] if name_node else "unknown"
                params = code[params_node.start_byte:params_node.end_byte] if params_node else "()"
                return f"{name}{params}"
                
            elif language in ['javascript', 'c', 'csharp']:
                # Similar logic for other languages
                name_node = node.child_by_field_name('name') 
                if name_node:
                    return code[name_node.start_byte:name_node.end_byte]
                    
        except Exception as e:
            self.logger.debug(f"Could not extract signature: {e}")
        
        return "unknown"
    
    def extract_class_methods(self, class_node, code: str, language: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract individual methods from a class definition."""
        methods = []
        method_types = self.METHOD_NODES.get(language, [])
        
        def find_methods_recursive(node):
            """Recursively find method nodes in class body."""
            if node.type in method_types:
                return [node]
            
            found_methods = []
            for child in node.children:
                found_methods.extend(find_methods_recursive(child))
            return found_methods
        
        # Find all method nodes within the class
        method_nodes = find_methods_recursive(class_node)
        
        for method_node in method_nodes:
            snippet = code[method_node.start_byte:method_node.end_byte]
            
            # Skip if method is too small (likely incomplete)
            if len(snippet.strip()) < 10:
                continue
                
            # Extract method metadata
            method_name = self.extract_node_name(method_node, code, language)
            signature = self.extract_function_signature(method_node, code, language)
            docstring = self.extract_docstring(method_node, code, language)
            
            method_unit = {
                "snippet": snippet,
                "span": [method_node.start_point[0] + 1, method_node.end_point[0] + 1],
                "start_byte": method_node.start_byte,
                "end_byte": method_node.end_byte,
                "node_type": method_node.type,
                "chunk_type": "method",
                "language": language,
                "name": method_name,
                "signature": signature,
                "parent_class": class_name,
                "qualified_name": f"{class_name}.{method_name}",
                "docstring": docstring,
                "chunk_size_bytes": len(snippet.encode('utf-8'))
            }
            
            methods.append(method_unit)
        
        return methods
    
    def extract_node_name(self, node, code: str, language: str) -> str:
        """Extract name/identifier from AST node."""
        try:
            if language in ['python', 'javascript', 'csharp']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    return code[name_node.start_byte:name_node.end_byte]
            
            elif language == 'c':
                if node.type == 'function_definition':
                    declarator = node.child_by_field_name('declarator')
                    if declarator and declarator.type == 'function_declarator':
                        name_node = declarator.child_by_field_name('declarator')
                        if name_node:
                            return code[name_node.start_byte:name_node.end_byte]
        except Exception as e:
            self.logger.debug(f"Could not extract name for node type {node.type}: {e}")
        
        return "unknown"
    
    def should_split_large_chunk(self, snippet: str) -> bool:
        """Determine if a chunk should be split due to size."""
        return len(snippet.encode('utf-8')) > self.MAX_CHUNK_SIZE
    
    def split_large_function(self, node, code: str, language: str) -> List[str]:
        """Split a large function into smaller logical chunks."""
        # For now, implement simple line-based splitting
        # Future enhancement: split on logical boundaries (statements, blocks)
        snippet = code[node.start_byte:node.end_byte]
        lines = snippet.split('\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line.encode('utf-8'))
            if current_size + line_size > self.TARGET_CHUNK_SIZE and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def extract_units(self, code: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract enhanced AST units with method-level granularity."""
        if language not in self.parsers:
            self.logger.warning(f"No parser available for language: {language}")
            return []
        
        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(code, 'utf-8'))
            root = tree.root_node
            
            units = []
            top_level_types = self.TOP_LEVEL_NODES[language]
            
            for child in root.children:
                if child.type in top_level_types:
                    
                    # Handle class definitions with method extraction
                    if child.type in ['class_definition', 'class_declaration']:
                        class_name = self.extract_node_name(child, code, language)
                        
                        # Create class-level chunk (header + metadata only)
                        class_snippet = self.extract_class_header(child, code, language)
                        docstring = self.extract_docstring(child, code, language)
                        
                        class_unit = {
                            "snippet": class_snippet,
                            "span": [child.start_point[0] + 1, child.end_point[0] + 1],
                            "start_byte": child.start_byte,
                            "end_byte": child.end_byte,
                            "node_type": child.type,
                            "chunk_type": "class",
                            "language": language,
                            "name": class_name,
                            "qualified_name": class_name,
                            "docstring": docstring,
                            "chunk_size_bytes": len(class_snippet.encode('utf-8'))
                        }
                        units.append(class_unit)
                        
                        # Extract individual methods
                        method_units = self.extract_class_methods(child, code, language, class_name)
                        units.extend(method_units)
                    
                    else:
                        # Handle non-class top-level nodes (functions, imports, etc.)
                        snippet = code[child.start_byte:child.end_byte]
                        node_name = self.extract_node_name(child, code, language)
                        
                        # Check if chunk is too large and needs splitting
                        if self.should_split_large_chunk(snippet) and child.type in self.METHOD_NODES.get(language, []):
                            # Split large functions
                            sub_chunks = self.split_large_function(child, code, language)
                            for i, sub_chunk in enumerate(sub_chunks):
                                unit = {
                                    "snippet": sub_chunk,
                                    "span": [child.start_point[0] + 1, child.end_point[0] + 1],
                                    "start_byte": child.start_byte,
                                    "end_byte": child.end_byte,
                                    "node_type": child.type,
                                    "chunk_type": "function_part",
                                    "language": language,
                                    "name": f"{node_name}_part_{i+1}",
                                    "qualified_name": f"{node_name}_part_{i+1}",
                                    "parent_function": node_name,
                                    "chunk_size_bytes": len(sub_chunk.encode('utf-8'))
                                }
                                units.append(unit)
                        else:
                            # Regular chunk
                            chunk_type = self.determine_chunk_type(child.type)
                            signature = self.extract_function_signature(child, code, language) if child.type in self.METHOD_NODES.get(language, []) else None
                            docstring = self.extract_docstring(child, code, language)
                            
                            unit = {
                                "snippet": snippet,
                                "span": [child.start_point[0] + 1, child.end_point[0] + 1],
                                "start_byte": child.start_byte,
                                "end_byte": child.end_byte,
                                "node_type": child.type,
                                "chunk_type": chunk_type,
                                "language": language,
                                "name": node_name,
                                "qualified_name": node_name,
                                "signature": signature,
                                "docstring": docstring,
                                "chunk_size_bytes": len(snippet.encode('utf-8'))
                            }
                            units.append(unit)
            
            return units
            
        except Exception as e:
            self.logger.error(f"Error extracting units from {file_path}: {e}")
            return []
    
    def extract_class_header(self, class_node, code: str, language: str) -> str:
        """Extract just the class definition header (no methods)."""
        # For now, extract first few lines up to class definition
        # Future enhancement: parse and extract only class signature + docstring
        snippet = code[class_node.start_byte:class_node.end_byte]
        lines = snippet.split('\n')
        
        # Take class definition line plus docstring if present
        header_lines = []
        in_docstring = False
        docstring_quotes = None
        
        for line in lines:
            header_lines.append(line)
            
            # Simple heuristic: stop after class definition + optional docstring
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_quotes = '"""' if '"""' in line else "'''"
                elif docstring_quotes in line:
                    break
            elif in_docstring:
                continue
            elif line.strip() and not line.startswith((' ', '\t')) and len(header_lines) > 1:
                # Hit another top-level declaration, stop
                header_lines = header_lines[:-1]
                break
            elif len(header_lines) > 10:  # Limit header size
                break
        
        return '\n'.join(header_lines)
    
    def determine_chunk_type(self, node_type: str) -> str:
        """Determine the semantic chunk type from AST node type."""
        type_mapping = {
            'function_definition': 'function',
            'function_declaration': 'function', 
            'class_definition': 'class',
            'class_declaration': 'class',
            'import_statement': 'import',
            'import_from_statement': 'import',
            'method_declaration': 'method',
            'assignment': 'constant',
            'variable_declaration': 'variable'
        }
        return type_mapping.get(node_type, 'other')
    
    def process_file(self, file_path: str, relative_to: str) -> List[Dict[str, Any]]:
        """Process a single file and extract enhanced AST units."""
        language = self.get_language_from_file(file_path)
        if not language:
            self.logger.debug(f"Skipping unsupported file: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            if not code.strip():
                self.logger.debug(f"Skipping empty file: {file_path}")
                return []
            
            units = self.extract_units(code, language, file_path)
            
            # Add normalized file path to all units
            normalized_path = self.normalize_file_path(file_path, relative_to)
            for unit in units:
                unit['file_path'] = file_path
                unit['normalized_path'] = normalized_path
            
            self.logger.info(f"Extracted {len(units)} enhanced units from {file_path}")
            return units
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    def find_code_files(self, root_dir: str) -> List[str]:
        """Recursively find all code files in the directory."""
        code_files = []
        supported_extensions = set(self.LANGUAGE_EXTENSIONS.keys())
        
        for root, dirs, files in os.walk(root_dir):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'build', 'dist']]
            
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    code_files.append(file_path)
        
        return code_files
    
    def create_output_structure(self, output_dir: str, file_path: str, relative_to: str) -> str:
        """Create organized output directory structure and a unique filename."""
        rel_path = os.path.relpath(file_path, relative_to)
        language = self.get_language_from_file(file_path)

        # Language directory (e.g. …/processed/code_enhanced/python)
        lang_dir = os.path.join(output_dir, language)
        os.makedirs(lang_dir, exist_ok=True)

        # Build a collision-free filename that flattens the whole relative path
        safe_rel = (
            Path(rel_path)
            .with_suffix('')           # drop extension
            .as_posix()                # ensure forward slashes
            .replace('/', '_')         # flatten into one component
            .replace(' ', '_')         # remove spaces
            .replace('-', '_')         # normalize dashes
        )

        output_file = os.path.join(lang_dir, f"{safe_rel}_enhanced_ast.json")
        return output_file
    
    def process_directory(self, input_dir: str, output_dir: str):
        """Process all code files in a directory and save enhanced AST units."""
        self.logger.info(f"Starting enhanced AST extraction from {input_dir}")
        
        # Find all code files
        code_files = self.find_code_files(input_dir)
        self.logger.info(f"Found {len(code_files)} code files to process")
        
        # Statistics tracking
        stats = {
            'total_files': len(code_files),
            'processed_files': 0,
            'total_units': 0,
            'chunk_type_counts': {},
            'size_distribution': {'small': 0, 'medium': 0, 'large': 0, 'oversized': 0},
            'by_language': {}
        }
        
        # Process each file
        for file_path in code_files:
            try:
                units = self.process_file(file_path, input_dir)
                
                if units:
                    # Create output file path
                    output_file = self.create_output_structure(output_dir, file_path, input_dir)
                    
                    # Save units to JSON file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(units, f, indent=2, ensure_ascii=False)
                    
                    # Update statistics
                    stats['processed_files'] += 1
                    stats['total_units'] += len(units)
                    
                    language = self.get_language_from_file(file_path)
                    if language not in stats['by_language']:
                        stats['by_language'][language] = {'files': 0, 'units': 0, 'avg_chunk_size': 0}
                    stats['by_language'][language]['files'] += 1
                    stats['by_language'][language]['units'] += len(units)
                    
                    # Analyze chunk sizes and types
                    total_size = 0
                    for unit in units:
                        chunk_type = unit.get('chunk_type', 'other')
                        stats['chunk_type_counts'][chunk_type] = stats['chunk_type_counts'].get(chunk_type, 0) + 1
                        
                        size = unit.get('chunk_size_bytes', 0)
                        total_size += size
                        
                        if size < 512:
                            stats['size_distribution']['small'] += 1
                        elif size < 2048:
                            stats['size_distribution']['medium'] += 1
                        elif size < 4096:
                            stats['size_distribution']['large'] += 1
                        else:
                            stats['size_distribution']['oversized'] += 1
                    
                    stats['by_language'][language]['avg_chunk_size'] = total_size // len(units) if units else 0
                    
                    self.logger.info(f"Saved {len(units)} enhanced units to {output_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
        
        # Save processing statistics
        stats_file = os.path.join(output_dir, 'enhanced_processing_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info("Enhanced AST extraction completed!")
        self.logger.info(f"Processed {stats['processed_files']}/{stats['total_files']} files")
        self.logger.info(f"Extracted {stats['total_units']} total enhanced AST units")
        self.logger.info(f"Chunk types: {stats['chunk_type_counts']}")
        self.logger.info(f"Size distribution: {stats['size_distribution']}")
        self.logger.info(f"Statistics saved to {stats_file}")


def main():
    """Main function to run enhanced AST extraction."""
    # Configuration
    repos_dir = "/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/repos"
    output_dir = "/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/processed/code_enhanced"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize and run enhanced extractor
    extractor = EnhancedASTExtractor()
    extractor.process_directory(repos_dir, output_dir)


if __name__ == "__main__":
    main()