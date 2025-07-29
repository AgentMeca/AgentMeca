#!/usr/bin/env python3
"""
AST Extractor for Code Files using Tree-sitter
Language-agnostic approach to extract top-level declarations from code files.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from tree_sitter import Parser
from tree_sitter_language_pack import get_language   # instead of tree_sitter_languages

class ASTExtractor:
    """Extract AST units from source code files using Tree-sitter."""
    
    # Language-specific node types for top-level declarations
    TOP_LEVEL_NODES = {
        'python': [
            'function_definition',
            'class_definition', 
            'import_statement',
            'import_from_statement'
        ],
        'javascript': [
            'function_declaration',
            'class_declaration',
            'export_statement',
            'import_statement',
            'variable_declaration'
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
        """Initialize the AST extractor with language parsers."""
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
    
    # only showing the modified method

    def setup_parsers(self):
        for lang in self.TOP_LEVEL_NODES:
            try:
                ts_lang = get_language(lang)
                
                # Try the new zero‑arg Parser + set_language() API
                try:
                    parser = Parser()
                    parser.set_language(ts_lang)
                except (AttributeError, TypeError):
                    # Fallback: old‑style constructor took the Language as argument
                    parser = Parser(ts_lang)

                self.parsers[lang] = parser
                self.logger.info(f"Loaded {lang} parser")
            except Exception as e:
                self.logger.error(f"Failed to load {lang} parser: {e}")

    
    def get_language_from_file(self, file_path: str) -> Optional[str]:
        """Determine the programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_EXTENSIONS.get(ext)
    
    def extract_units(self, code: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract AST units from source code."""
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
                    snippet = code[child.start_byte:child.end_byte]
                    
                    # Extract additional metadata based on node type
                    metadata = self.extract_node_metadata(child, code, language)
                    
                    unit = {
                        "snippet": snippet,
                        "span": [child.start_point[0] + 1, child.end_point[0] + 1],
                        "start_byte": child.start_byte,
                        "end_byte": child.end_byte,
                        "node_type": child.type,
                        "language": language,
                        "file_path": file_path,
                        **metadata
                    }
                    units.append(unit)
            
            return units
            
        except Exception as e:
            self.logger.error(f"Error extracting units from {file_path}: {e}")
            return []
    
    def extract_node_metadata(self, node, code: str, language: str) -> Dict[str, Any]:
        """Extract additional metadata from AST nodes."""
        metadata = {}
        
        try:
            # Extract name/identifier if available
            if language == 'python':
                if node.type in ['function_definition', 'class_definition']:
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        metadata['name'] = code[name_node.start_byte:name_node.end_byte]
            
            elif language == 'javascript':
                if node.type in ['function_declaration', 'class_declaration']:
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        metadata['name'] = code[name_node.start_byte:name_node.end_byte]
            
            elif language == 'c':
                if node.type == 'function_definition':
                    declarator = node.child_by_field_name('declarator')
                    if declarator and declarator.type == 'function_declarator':
                        name_node = declarator.child_by_field_name('declarator')
                        if name_node:
                            metadata['name'] = code[name_node.start_byte:name_node.end_byte]
            
            elif language == 'csharp':
                if node.type in ['class_declaration', 'method_declaration', 'namespace_declaration']:
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        metadata['name'] = code[name_node.start_byte:name_node.end_byte]
        
        except Exception as e:
            self.logger.debug(f"Could not extract metadata for node type {node.type}: {e}")
        
        return metadata
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file and extract AST units."""
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
            self.logger.info(f"Extracted {len(units)} units from {file_path}")
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
        language  = self.get_language_from_file(file_path)

        # Language directory (e.g. …/processed/code/python)
        lang_dir = os.path.join(output_dir, language)
        os.makedirs(lang_dir, exist_ok=True)

        # ── NEW: build a collision‑free filename that flattens the whole relative path ──
        #   repos/AsyrilDemo/main.py      →  AsyrilDemo_main
        #   repos/sample-programs/Python/TCP-Socket-Client/main.py
        #                                    →  sample-programs_Python_TCP-Socket-Client_main
        safe_rel = (
            Path(rel_path)
            .with_suffix('')           # drop extension
            .as_posix()                # ensure forward slashes
            .replace('/', '_')         # flatten into one component
        )

        output_file = os.path.join(lang_dir, f"{safe_rel}_ast.json")
        return output_file

    
    def process_directory(self, input_dir: str, output_dir: str):
        """Process all code files in a directory and save AST units."""
        self.logger.info(f"Starting AST extraction from {input_dir}")
        
        # Find all code files
        code_files = self.find_code_files(input_dir)
        self.logger.info(f"Found {len(code_files)} code files to process")
        
        # Statistics tracking
        stats = {
            'total_files': len(code_files),
            'processed_files': 0,
            'total_units': 0,
            'by_language': {}
        }
        
        # Process each file
        for file_path in code_files:
            try:
                units = self.process_file(file_path)
                
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
                        stats['by_language'][language] = {'files': 0, 'units': 0}
                    stats['by_language'][language]['files'] += 1
                    stats['by_language'][language]['units'] += len(units)
                    
                    self.logger.info(f"Saved {len(units)} units to {output_file}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
        
        # Save processing statistics
        stats_file = os.path.join(output_dir, 'processing_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info("AST extraction completed!")
        self.logger.info(f"Processed {stats['processed_files']}/{stats['total_files']} files")
        self.logger.info(f"Extracted {stats['total_units']} total AST units")
        self.logger.info(f"Statistics saved to {stats_file}")


def main():
    """Main function to run AST extraction."""
    # Configuration
    repos_dir = "/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/repos"
    output_dir = "/mnt/d/OneDrive/OneDrive - purdue.edu/Documents/Work/Mecademic/AgentMeca/processed/code"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize and run extractor
    extractor = ASTExtractor()
    extractor.process_directory(repos_dir, output_dir)


if __name__ == "__main__":
    main()