# AgentMeca - Unified Workspace

This repository contains a comprehensive collection of Mecademic robotics projects, demos, utilities, and documentation organized in a single workspace. It includes an advanced **RAG (Retrieval-Augmented Generation) system** that provides semantic search and analysis capabilities across all Mecademic code and documentation.

## Repository Structure

### Demo Projects
- **AsyrilDemo** - Demo with the Meca500 and Asycube240
- **ATX2023Zaber** - Zaber Demo for the ATX 2023 Trade show
- **Demo_Glove_Box** - Code for the SLAS 2022 demo of the robot in the glove box
- **Demo_Microscope** - Demo for the microscope for SALS
- **Demo_Well_Plates** - Code for the well plates demo for the SLAS show
- **MecaDashboard** - Dashboard application for Mecademic robots
- **RAMInsertion** - Force functions with the ATI force sensor
- **SLAS2025** - Repo for the SLAS2025 full demo

### Libraries and APIs
- **mecademicpy** - Mecademic Python API
- **utilities** - Software for working with various sensors and components compatible with Mecademic robots

### Integration and Examples
- **meca500-accessories** - Integration code and documentation for Meca500 with various accessories including feeder systems, end-of-arm tooling, vision systems, and more
- **sample-programs** - Software program examples and demos for the robots at Mecademic

### Documentation
- **mcs500_mecaportal_manual.pdf** - MCS500 MecaPortal Manual
- **mcs500_programming_manual.pdf** - MCS500 Programming Manual  
- **mcs500_user_manual.pdf** - MCS500 User Manual
- **meca500_mecaportal_manual.pdf** - Meca500 MecaPortal Manual
- **meca500_programming_manual.pdf** - Meca500 Programming Manual
- **meca500_user_manual.pdf** - Meca500 User Manual
- **megp25_gripper_manual.pdf** - MEGP25 Gripper Manual
- **mpm500_pneumatic_module_manual.pdf** - MPM500 Pneumatic Module Manual
- **mvk01_module_manual.pdf** - MVK01 Module Manual

### RAG Processing System
- **semantic_processing_pipeline.py** - Unified semantic processing pipeline for documents and code
- **enhanced_ast_extractor.py** - Tree-sitter based AST extraction with method-level granularity
- **semantic_code_chunker.py** - Code-specific semantic chunking with hash-based IDs
- **semantic_text_chunker.py** - Document semantic chunking with token optimization
- **pdf_processor.py** - PDF document processing and text extraction
- **chunk_quality_validator.py** - Quality validation and reporting for semantic chunks
- **processed/** - Directory containing all processed semantic chunks and metadata

### Vector Database System
- **vector_database.py** - Main ChromaDB interface with dual embedding models
- **ingest_chunks.py** - Batch ingestion pipeline for semantic chunks
- **vector_db_manager.py** - CLI management tool for database operations
- **vector_db_config.yaml** - Configuration file for embeddings and database settings

## RAG (Retrieval-Augmented Generation) System

### Overview

This repository includes a production-ready RAG system that processes Mecademic's entire codebase and documentation into semantically meaningful chunks with full vector database capabilities. The system provides:

- **Semantic Code Analysis**: Method-level granularity with function signatures, docstrings, and type information
- **Document Processing**: PDF manuals converted to token-optimized semantic chunks
- **Multi-language Support**: Python, JavaScript, C, and C# code processing
- **Vector Database**: ChromaDB with dual embedding models (BGE-M3 for docs, StarCoder2-15B for code)
- **Semantic Search**: High-performance similarity search across all content types
- **Quality Validation**: Comprehensive chunk quality reporting and metrics
- **Structured Metadata**: Hash-based IDs, symbol names, qualified names, and location tracking

### Current Status

✅ **Processing Complete**: 2,239 semantic chunks generated from 107 files  
✅ **Code Chunks**: 2,216 chunks across 4 programming languages  
✅ **Document Chunks**: 23 semantic chunks from PDF manuals  
✅ **Quality Validated**: 91.30% token range compliance for documents  
✅ **Vector Database**: Complete ChromaDB implementation with dual embedding models

### Processed Content Structure

```
processed/
├── semantic_chunks/
│   ├── code/                    # Code semantic chunks (2,216 chunks)
│   │   ├── *_semantic_chunks.jsonl
│   └── docs/                    # Document semantic chunks (23 chunks)
│       ├── *_semantic_chunks.jsonl
├── code_enhanced/               # Enhanced AST extractions
│   ├── python/, javascript/, c/, csharp/
└── docs/                        # PDF processing outputs
```

### Language Distribution

- **Python**: 2,122 chunks (mecademicpy, demo applications, utilities)
- **JavaScript**: 45 chunks (MecaDashboard React components)
- **C**: 35 chunks (TCP communication, robot interface)
- **C#**: 14 chunks (FlexiBowl integration, Meca500 quickstart)

### Chunk Types and Metadata

Each semantic chunk includes:
- **Unique Hash ID**: SHA1-based collision-resistant identifiers
- **Symbol Information**: Function/class names, qualified names, signatures
- **Location Data**: File paths, line numbers, byte positions
- **Content Metadata**: Docstrings, chunk types, language detection
- **Quality Metrics**: Size optimization (mean 535.9 bytes for code chunks)

## Getting Started

Each project directory contains its own README with specific setup and usage instructions.

### RAG System Usage

#### Vector Database Operations

1. **Setup and Ingestion**:
   ```bash
   python vector_db_manager.py health        # Check system status
   python vector_db_manager.py ingest        # Ingest all chunks
   python vector_db_manager.py stats         # View database statistics
   ```

2. **Search Operations**:
   ```bash
   python vector_db_manager.py search "robot connection examples"
   python vector_db_manager.py search "gripper control" --limit 10
   ```

3. **Database Management**:
   ```bash
   python vector_db_manager.py backup        # Create backup
   python vector_db_manager.py reset         # Reset database
   ```

#### Running the Semantic Processing Pipeline

1. **Process All Content** (documents + code):
   ```bash
   python semantic_processing_pipeline.py
   ```

2. **Process Only Documents**:
   ```bash
   python semantic_processing_pipeline.py --docs-only
   ```

3. **Process Only Code**:
   ```bash
   python semantic_processing_pipeline.py --code-only
   ```

4. **Run with Validation**:
   ```bash
   python semantic_processing_pipeline.py --validate
   ```

#### Processing Individual Components

- **Enhanced AST Extraction**:
  ```bash
  python enhanced_ast_extractor.py
  ```

- **Quality Validation**:
  ```bash
  python chunk_quality_validator.py
  ```

#### Output Files and Formats

- **Semantic Chunks**: JSONL format in `processed/semantic_chunks/`
- **Processing Reports**: JSON and text summaries in `processed/semantic_chunks/`
- **Quality Reports**: `chunk_quality_report.json` and `.txt`
- **Vector Database**: ChromaDB collection in `chroma_db/`

#### Chunk Format Example

```json
{
  "chunk_id": "meca_samples:mecademicpy/robot.py:a1b2c3d4e5f6",
  "repo": "meca_samples",
  "lang": "python",
  "symbol": "Robot.connect",
  "qualified_name": "Robot.connect",
  "source_path": "mecademicpy/robot.py",
  "loc": [145, 167],
  "text": "def connect(self, address='192.168.0.100', timeout=30):\n    \"\"\"Connect to robot at specified IP address.\"\"\"\n    # Implementation...",
  "hash": "a1b2c3d4e5f6",
  "chunk_type": "method",
  "signature": "connect(self, address='192.168.0.100', timeout=30)",
  "docstring": "Connect to robot at specified IP address."
}
```

## Contributing

When working on individual projects:
1. Make changes in the appropriate project directory
2. Test your changes locally
3. Commit to this repository
4. For upstream contributions, create pull requests to the original repositories in the AgentMeca organization

## Vector Database Architecture

### 🎯 Implementation Complete
- **ChromaDB Integration**: Production-ready vector database with persistent storage
- **Dual Embedding Models**: BGE-M3 for documents, StarCoder2-15B for code
- **Content-Type Routing**: Automatic model selection based on content type
- **Batch Processing**: Efficient ingestion with progress tracking and error handling
- **CLI Management**: Complete command-line interface for all operations

### 📊 Technical Specifications
- **Database**: ChromaDB with persistent local storage
- **Embedding Models**: 
  - BGE-M3 (1024-dim) for 23 document chunks
  - StarCoder2-15B (1536-dim) for 2,216 code chunks
- **Search Performance**: Sub-second similarity search across all content
- **Metadata Rich**: Function signatures, docstrings, and semantic relationships
- **Languages Supported**: Python, JavaScript, C, C#
- **Document Coverage**: All Mecademic manuals and programming guides

### 🚀 Available Features
- **Semantic Search**: High-performance similarity search with configurable results
- **Content Filtering**: Search within specific content types (code vs documents)
- **Metadata Queries**: Search by language, file type, or semantic properties
- **Database Management**: Backup, restore, reset, and health monitoring
- **Statistics**: Comprehensive database metrics and collection information

## Organization

This workspace is maintained by the AgentMeca organization on GitHub.