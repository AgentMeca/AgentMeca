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

## RAG (Retrieval-Augmented Generation) System

### Overview

This repository includes a production-ready RAG system that processes Mecademic's entire codebase and documentation into semantically meaningful chunks optimized for AI-powered search and analysis. The system provides:

- **Semantic Code Analysis**: Method-level granularity with function signatures, docstrings, and type information
- **Document Processing**: PDF manuals converted to token-optimized semantic chunks
- **Multi-language Support**: Python, JavaScript, C, and C# code processing
- **Quality Validation**: Comprehensive chunk quality reporting and metrics
- **Structured Metadata**: Hash-based IDs, symbol names, qualified names, and location tracking

### Current Status

✅ **Processing Complete**: 2,239 semantic chunks generated from 107 files  
✅ **Code Chunks**: 2,216 chunks across 4 programming languages  
✅ **Document Chunks**: 23 semantic chunks from PDF manuals  
✅ **Quality Validated**: 91.30% token range compliance for documents  
🔄 **Next Phase**: Vector database integration (in progress)

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

## Next Steps: Vector Database Integration

The RAG system is currently in the vector database integration phase. Planned components include:

### 🔄 In Progress
- **Vector Database Setup**: ChromaDB or Pinecone integration for semantic chunk storage
- **Embedding Generation**: Generate embeddings for all 2,239 semantic chunks
- **Similarity Search**: Implement semantic search across code and documentation
- **Query Interface**: Build API endpoints for RAG-powered queries

### 🎯 Upcoming Features
- **Contextual Code Search**: "Find examples of robot connection handling"
- **Cross-Reference Analysis**: Link related functions across different projects
- **Documentation Q&A**: Answer questions using both code and manual references
- **Code Generation Assistance**: RAG-augmented code suggestions and examples

### 📊 Technical Specifications
- **Chunk Count**: 2,239 ready for embedding
- **Languages Supported**: Python, JavaScript, C, C#
- **Document Coverage**: All Mecademic manuals and programming guides
- **Metadata Rich**: Function signatures, docstrings, and semantic relationships

## Organization

This workspace is maintained by the AgentMeca organization on GitHub.