#!/usr/bin/env python3
"""
Vector Database Management CLI

Command-line interface for managing the vector database: ingestion, search,
statistics, backup, and maintenance operations.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import shutil

from vector_database import create_database
from ingest_chunks import ChunkIngester


class VectorDBManager:
    """
    CLI manager for vector database operations.
    """
    
    def __init__(self, config_path: str = "vector_db_config.yaml"):
        """
        Initialize the database manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.db = None
        
    def _get_database(self):
        """Get database instance (lazy initialization)."""
        if self.db is None:
            self.db = create_database(self.config_path)
        return self.db
    
    def cmd_ingest(self, args) -> int:
        """Ingest chunks from JSONL files."""
        print("Starting chunk ingestion...")
        
        try:
            ingester = ChunkIngester(self.config_path)
            
            stats = ingester.ingest_from_directory(
                source_dir=args.source_dir,
                batch_size=args.batch_size
            )
            
            # Generate report if requested
            if args.report:
                ingester.write_ingestion_report(stats)
                print(f"Detailed report written to: {ingester.config['storage']['log_directory']}")
            
            # Print summary
            print(f"\nIngestion Complete:")
            print(f"  Files processed: {stats['files_processed']}")
            print(f"  Chunks loaded: {stats['chunks_loaded']}")
            print(f"  Chunks ingested: {stats['chunks_ingested']}")
            print(f"  Chunks skipped: {stats['chunks_skipped']}")
            print(f"  Processing time: {stats['processing_time_seconds']:.1f}s")
            print(f"  Success rate: {stats['success_rate']:.2%}")
            
            # Content type distribution
            if stats['content_type_distribution']:
                print(f"\nContent Distribution:")
                for content_type, count in stats['content_type_distribution'].items():
                    print(f"  {content_type}: {count}")
            
            # Show errors if any
            if stats['errors']:
                print(f"\nErrors ({len(stats['errors'])}):")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
                if len(stats['errors']) > 5:
                    print(f"  ... and {len(stats['errors']) - 5} more errors")
            
            return 0
            
        except Exception as e:
            print(f"Error during ingestion: {e}")
            return 1
    
    def cmd_search(self, args) -> int:
        """Search for similar chunks."""
        try:
            db = self._get_database()
            
            print(f"Searching for: '{args.query}'")
            if args.content_type:
                print(f"Content type filter: {args.content_type}")
            
            start_time = time.time()
            results = db.search(
                query=args.query,
                content_type=args.content_type,
                limit=args.limit,
                similarity_threshold=args.threshold
            )
            search_time = time.time() - start_time
            
            print(f"\nFound {len(results)} results in {search_time:.3f}s")
            print("-" * 60)
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                similarity = result['similarity_score']
                text = result['text']
                
                print(f"\n{i}. Score: {similarity:.3f}")
                print(f"   Type: {metadata.get('content_type', 'unknown')}")
                
                if metadata.get('source'):
                    print(f"   Source: {metadata['source']}")
                elif metadata.get('source_path'):
                    print(f"   File: {metadata['source_path']}")
                
                if metadata.get('symbol'):
                    print(f"   Symbol: {metadata['symbol']}")
                    
                # Show text preview
                text_preview = text[:200] + "..." if len(text) > 200 else text
                print(f"   Text: {text_preview}")
            
            return 0
            
        except Exception as e:
            print(f"Error during search: {e}")
            return 1
    
    def cmd_stats(self, args) -> int:
        """Show database statistics."""
        try:
            db = self._get_database()
            stats = db.get_stats()
            
            print("Vector Database Statistics")
            print("=" * 30)
            print(f"Database path: {stats['database_path']}")
            print(f"Collection: {stats['collection_name']}")
            print(f"Total chunks: {stats['total_chunks']:,}")
            print(f"Document chunks: {stats['document_chunks']:,}")
            print(f"Code chunks: {stats['code_chunks']:,}")
            
            # Model loading status
            models = stats['models_loaded']
            print(f"\nModels loaded:")
            print(f"  Document model (BGE-M3): {'✓' if models['document_model'] else '✗'}")
            print(f"  Code model (StarCoder2): {'✓' if models['code_model'] else '✗'}")
            
            # Cache statistics if available
            if 'embedding_cache_hits' in stats:
                total_requests = stats['embedding_cache_hits'] + stats['embedding_cache_misses']
                if total_requests > 0:
                    hit_rate = stats['embedding_cache_hits'] / total_requests
                    print(f"\nEmbedding cache:")
                    print(f"  Hit rate: {hit_rate:.2%}")
                    print(f"  Hits: {stats['embedding_cache_hits']:,}")
                    print(f"  Misses: {stats['embedding_cache_misses']:,}")
            
            return 0
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return 1
    
    def cmd_validate(self, args) -> int:
        """Validate database integrity."""
        try:
            db = self._get_database()
            
            print("Validating database integrity...")
            
            # Get basic stats
            stats = db.get_stats()
            total_chunks = stats['total_chunks']
            
            if total_chunks == 0:
                print("Database is empty - nothing to validate")
                return 0
            
            print(f"Validating {total_chunks:,} chunks...")
            
            # Test search functionality
            print("Testing search functionality...")
            try:
                # Simple search test
                test_results = db.search("robot", limit=5)
                print(f"  ✓ Search test passed - returned {len(test_results)} results")
            except Exception as e:
                print(f"  ✗ Search test failed: {e}")
                return 1
            
            # Check content type distribution
            doc_chunks = stats['document_chunks']
            code_chunks = stats['code_chunks']
            
            if doc_chunks + code_chunks != total_chunks:
                print(f"  ⚠ Content type mismatch: {doc_chunks} + {code_chunks} ≠ {total_chunks}")
            else:
                print(f"  ✓ Content type distribution correct")
            
            print("\nDatabase validation completed successfully")
            return 0
            
        except Exception as e:
            print(f"Error during validation: {e}")
            return 1
    
    def cmd_backup(self, args) -> int:
        """Create database backup."""
        try:
            db = self._get_database()
            
            # Create backup directory
            backup_dir = Path(db.config['storage']['backup_directory'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"vector_db_backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            # Copy database directory
            db_path = Path(db.config['database']['path'])
            if db_path.exists():
                print(f"Creating backup: {backup_path}")
                shutil.copytree(db_path, backup_path)
                
                # Create backup manifest
                manifest = {
                    "timestamp": timestamp,
                    "database_path": str(db_path),
                    "backup_path": str(backup_path),
                    "stats": db.get_stats()
                }
                
                with open(backup_path / "backup_manifest.json", 'w') as f:
                    json.dump(manifest, f, indent=2, default=str)
                
                print(f"Backup created successfully: {backup_path}")
                return 0
            else:
                print("Database directory does not exist - nothing to backup")
                return 1
                
        except Exception as e:
            print(f"Error creating backup: {e}")
            return 1
    
    def cmd_reset(self, args) -> int:
        """Reset database (delete all data)."""
        if not args.force:
            response = input("This will delete all data in the database. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Reset cancelled")
                return 0
        
        try:
            db = self._get_database()
            db.reset_database()
            print("Database reset successfully")
            return 0
            
        except Exception as e:
            print(f"Error resetting database: {e}")
            return 1
    
    def cmd_health(self, args) -> int:
        """Perform health check."""
        try:
            print("Performing health check...")
            
            # Check if config file exists
            if not Path(self.config_path).exists():
                print(f"✗ Configuration file not found: {self.config_path}")
                return 1
            print(f"✓ Configuration file exists: {self.config_path}")
            
            # Try to initialize database
            try:
                db = self._get_database()
                print("✓ Database connection successful")
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                return 1
            
            # Check database path
            db_path = Path(db.config['database']['path'])
            if db_path.exists():
                print(f"✓ Database directory exists: {db_path}")
            else:
                print(f"⚠ Database directory does not exist: {db_path}")
            
            # Get stats
            stats = db.get_stats()
            print(f"✓ Database stats retrieved: {stats['total_chunks']} chunks")
            
            # Check if models can be loaded
            try:
                # This will trigger lazy loading
                _ = db.document_model
                print("✓ Document model (BGE-M3) loaded successfully")
            except Exception as e:
                print(f"✗ Document model failed to load: {e}")
            
            try:
                _ = db.code_model
                print("✓ Code model (StarCoder2-15B) loaded successfully")
            except Exception as e:
                print(f"✗ Code model failed to load: {e}")
            
            print("\nHealth check completed")
            return 0
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Vector Database Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config", 
        default="vector_db_config.yaml", 
        help="Configuration file path"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest chunks from JSONL files')
    ingest_parser.add_argument('--source-dir', help='Directory containing JSONL files')
    ingest_parser.add_argument('--batch-size', type=int, default=100, help='Batch size for processing')
    ingest_parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for similar chunks')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--content-type', choices=['document', 'code'], help='Filter by content type')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
    search_parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate database integrity')
    
    # Backup command
    subparsers.add_parser('backup', help='Create database backup')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database (delete all data)')
    reset_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    # Health command
    subparsers.add_parser('health', help='Perform health check')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize manager and run command
    manager = VectorDBManager(args.config)
    
    # Route to appropriate command handler
    command_handlers = {
        'ingest': manager.cmd_ingest,
        'search': manager.cmd_search,
        'stats': manager.cmd_stats,
        'validate': manager.cmd_validate,
        'backup': manager.cmd_backup,
        'reset': manager.cmd_reset,
        'health': manager.cmd_health
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())