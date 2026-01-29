"""
CLI Interface Module
Handles command line argument parsing and main program flow.
"""

import argparse
import sys
import json
from dataforge.logger import setup_logger, log_start, log_completion
from dataforge.config import load_default_config, merge_config_with_args
from dataforge.utils import load_schema
from dataforge.validator import validate_all_parameters
from dataforge.schema_parser import parse_schema
from dataforge.data_generator import create_generator
from dataforge.file_manager import create_multiple_files, clear_directory, write_to_console
from dataforge.multiprocessor import generate_files_parallel, should_use_multiprocessing


def create_parser():
    """
    Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog='dataforge',
        description='DataForge - Test Data Generation Utility\n'
                    'Generate test JSON data based on custom data schemas for testing data pipelines.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Generate 3 files in current directory:
    dataforge . --files_count=3 --file_name=data --file_prefix=count

  Load schema from file:
    dataforge ./output --data_schema=./schema.json

  Output to console:
    dataforge . --files_count=0 --data_lines=10

  Parallel generation:
    dataforge ./output --files_count=100 --multiprocessing=4
        '''
    )
    
    # Positional argument
    parser.add_argument(
        'path_to_save_files',
        type=str,
        help="Path where files will be saved (relative or absolute). Use '.' for current directory."
    )
    
    # Optional arguments
    parser.add_argument(
        '--files_count',
        type=int,
        help='Number of files to generate. Use 0 to output to console. (default: from config)'
    )
    
    parser.add_argument(
        '--file_name',
        type=str,
        help='Base name for generated files (default: from config)'
    )
    
    parser.add_argument(
        '--file_prefix',
        type=str,
        choices=['count', 'random', 'uuid'],
        help='Prefix strategy for file names: count (sequential), random (random numbers), uuid (unique IDs)'
    )
    
    parser.add_argument(
        '--data_schema',
        type=str,
        help='JSON schema string or path to JSON file containing schema'
    )
    
    parser.add_argument(
        '--data_lines',
        type=int,
        help='Number of data lines to generate in each file (default: from config)'
    )
    
    parser.add_argument(
        '--clear_path',
        action='store_true',
        help='Delete existing files with matching name before generation'
    )
    
    parser.add_argument(
        '--multiprocessing',
        type=int,
        help='Number of parallel processes to use for file generation (default: from config)'
    )
    
    return parser


def parse_arguments(args=None):
    """
    Parse command line arguments.
    
    Args:
        args (list, optional): Arguments to parse. If None, uses sys.argv
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = create_parser()
    return parser.parse_args(args)


def display_parameters(logger, params):
    """
    Display current parameters configuration.
    
    Args:
        logger: Logger instance
        params (dict): Parameters dictionary
    """
    logger.info("Current configuration:")
    logger.info(f"  Path to save files: {params['path_to_save_files']}")
    logger.info(f"  Files count: {params['files_count']}")
    logger.info(f"  File name: {params['file_name']}")
    logger.info(f"  File prefix: {params['file_prefix']}")
    logger.info(f"  Data lines per file: {params['data_lines']}")
    logger.info(f"  Multiprocessing: {params['multiprocessing']} process(es)")
    logger.info(f"  Clear path: {params['clear_path']}")
    
    if params['data_schema']:
        # Convert dict to string for display
        import json
        schema_str = json.dumps(params['data_schema'])
        schema_preview = schema_str[:100]
        if len(schema_str) > 100:
            schema_preview += "..."
        logger.info(f"  Data schema: {schema_preview}")


def main():
    """
    Main entry point for the application.
    
    This function:
    1. Sets up logging
    2. Loads configuration from default.ini
    3. Parses command line arguments
    4. Merges configuration with arguments (CLI has priority)
    5. Validates parameters
    6. Executes data generation (to be implemented in later stages)
    """
    # Setup logger
    logger = setup_logger()
    
    try:
        # Log application start
        log_start(logger, "DataForge - Test Data Generation Utility")
        
        # Load configuration from default.ini
        logger.info("Loading configuration from default.ini...")
        config = load_default_config()
        
        # Parse command line arguments
        logger.info("Parsing command line arguments...")
        args = parse_arguments()
        
        # Merge configuration with CLI arguments (CLI has priority)
        logger.info("Merging configuration with command line arguments...")
        params = merge_config_with_args(config, args)
        
        # Load schema before validation (from file or string -> dict)
        if params.get('data_schema'):
            if isinstance(params['data_schema'], str):
                logger.info("Loading data schema...")
                params['data_schema'] = load_schema(params['data_schema'])
        
        # Validate all parameters (schema is now a dict)
        logger.info("Validating all parameters...")
        params = validate_all_parameters(params)
        
        # Parse schema (convert to internal representation)
        if params.get('data_schema'):
            logger.info("Parsing data schema...")
            params['parsed_schema'] = parse_schema(params['data_schema'])
            logger.info(f"Schema parsed: {len(params['parsed_schema'])} field(s) defined")
        
        # Display current configuration
        display_parameters(logger, params)
        
        # Create data generator
        logger.info("=" * 60)
        logger.info("Starting data generation...")
        logger.info("=" * 60)
        
        generator = create_generator(params['parsed_schema'])
        logger.info(f"Generator initialized for {len(params['parsed_schema'])} field(s)")
        
        # Generate data
        if params['files_count'] == 0:
            # Console output mode
            logger.info("Mode: Console output")
            logger.info(f"Generating {params['data_lines']} line(s)...")
            
            lines = generator.generate_lines(params['data_lines'])
            
            logger.info("-" * 60)
            logger.info("Generated data:")
            logger.info("-" * 60)
            
            write_to_console(lines)
            
            logger.info("-" * 60)
            logger.info(f"Total lines generated: {len(lines)}")
        
        else:
            # File output mode
            logger.info(f"Mode: File output ({params['files_count']} file(s))")
            logger.info(f"Lines per file: {params['data_lines']}")
            logger.info(f"Output directory: {params['path_to_save_files']}")
            logger.info(f"File prefix type: {params['file_prefix']}")
            logger.info("")
            
            # Clear directory if requested
            if params['clear_path']:
                logger.info("Clearing existing JSON files from output directory...")
                removed = clear_directory(params['path_to_save_files'], '*.json')
                if removed > 0:
                    logger.info(f"Removed {removed} existing file(s)")
            
            # Decide whether to use multiprocessing
            use_multiprocessing = should_use_multiprocessing(
                params['files_count'], 
                params['multiprocessing']
            )
            
            # Create files
            if use_multiprocessing:
                logger.info(f"Creating files using {params['multiprocessing']} parallel process(es)...")
                
                # Prepare parameters for parallel generation
                parallel_params = {
                    'path': params['path_to_save_files'],
                    'file_name': params['file_name'],
                    'prefix_type': params['file_prefix'],
                    'files_count': params['files_count'],
                    'data_lines': params['data_lines'],
                    'multiprocessing': params['multiprocessing'],
                    'parsed_schema': params['parsed_schema']
                }
                
                created_files = generate_files_parallel(parallel_params)
            else:
                logger.info("Creating files (single process mode)...")
                created_files = create_multiple_files(
                    path=params['path_to_save_files'],
                    file_name=params['file_name'],
                    prefix_type=params['file_prefix'],
                    files_count=params['files_count'],
                    data_lines_per_file=params['data_lines'],
                    generator=generator
                )
            
            logger.info("-" * 60)
            logger.info(f"Successfully created {len(created_files)} file(s):")
            
            # Show first 5 files
            for i, filepath in enumerate(created_files[:5], 1):
                import os
                filename = os.path.basename(filepath)
                logger.info(f"  {i}. {filename}")
            
            if len(created_files) > 5:
                logger.info(f"  ... and {len(created_files) - 5} more file(s)")
            
            logger.info("-" * 60)
            logger.info(f"Total data lines written: {params['files_count'] * params['data_lines']}")
        
        # Log completion
        log_completion(logger)
        logger.info("=" * 60)
        logger.info("Data generation completed successfully")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("\nOperation interrupted by user (Ctrl+C)")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
