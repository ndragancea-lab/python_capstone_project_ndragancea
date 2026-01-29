"""
Multiprocessor Module
Handles parallel file generation using multiprocessing.

This module distributes file generation work across multiple processes
to improve performance for large batch operations.
"""

import os
from multiprocessing import Pool
from dataforge.logger import get_logger
from dataforge.data_generator import create_generator
from dataforge.file_manager import create_single_file


def distribute_work(total_files, num_processes):
    """
    Distribute file generation work across processes.
    
    Args:
        total_files (int): Total number of files to create
        num_processes (int): Number of processes to use
    
    Returns:
        list[int]: List with number of files for each process
    
    Example:
        >>> distribute_work(10, 3)
        [4, 3, 3]
        
        >>> distribute_work(7, 2)
        [4, 3]
        
        >>> distribute_work(5, 5)
        [1, 1, 1, 1, 1]
    """
    logger = get_logger()
    
    # Calculate base files per process
    files_per_process = total_files // num_processes
    remainder = total_files % num_processes
    
    # Distribute work
    distribution = []
    for i in range(num_processes):
        # First 'remainder' processes get one extra file
        if i < remainder:
            distribution.append(files_per_process + 1)
        else:
            distribution.append(files_per_process)
    
    logger.debug(f"Work distribution for {total_files} files across {num_processes} processes: {distribution}")
    
    return distribution


def worker_function(args):
    """
    Worker function for parallel file generation.
    
    This function is called by each process in the pool.
    
    Args:
        args (tuple): (process_id, files_to_create, common_params)
            - process_id (int): ID of this worker process
            - files_to_create (int): Number of files this worker should create
            - common_params (dict): Common parameters for file generation
    
    Returns:
        list[str]: List of created file paths
    
    Example:
        >>> args = (1, 2, {
        ...     'path': '/tmp',
        ...     'file_name': 'data',
        ...     'prefix_type': 'count',
        ...     'data_lines': 10,
        ...     'parsed_schema': {...}
        ... })
        >>> files = worker_function(args)
    """
    process_id, files_to_create, common_params = args
    
    # Get logger (each process needs its own logger instance)
    logger = get_logger()
    
    logger.debug(f"Process {process_id}: Starting, will create {files_to_create} file(s)")
    
    # Create generator for this process
    generator = create_generator(common_params['parsed_schema'])
    
    # Calculate starting index for this process
    # Each process gets a unique range of indices
    start_index = common_params.get('start_index', 1)
    
    created_files = []
    
    for i in range(files_to_create):
        # Calculate file index
        file_index = start_index + i
        
        # Generate data for this file
        data_lines = generator.generate_lines(common_params['data_lines'])
        
        # Create file parameters
        file_params = {
            'path': common_params['path'],
            'file_name': common_params['file_name'],
            'prefix_type': common_params['prefix_type'],
            'index': file_index,
            'data': data_lines
        }
        
        # Create the file
        filepath = create_single_file(file_params)
        created_files.append(filepath)
        
        logger.debug(f"Process {process_id}: Created file {i+1}/{files_to_create}: {os.path.basename(filepath)}")
    
    logger.debug(f"Process {process_id}: Completed, created {len(created_files)} file(s)")
    
    return created_files


def generate_files_parallel(params):
    """
    Generate files in parallel using multiprocessing.
    
    Args:
        params (dict): Parameters dictionary containing:
            - path (str): Directory path
            - file_name (str): Base file name
            - prefix_type (str): Prefix type ('count', 'random', 'uuid')
            - files_count (int): Total number of files to create
            - data_lines (int): Number of data lines per file
            - multiprocessing (int): Number of processes to use
            - parsed_schema (dict): Parsed schema for data generation
    
    Returns:
        list[str]: List of all created file paths
    
    Example:
        >>> params = {
        ...     'path': '/tmp',
        ...     'file_name': 'data',
        ...     'prefix_type': 'count',
        ...     'files_count': 10,
        ...     'data_lines': 100,
        ...     'multiprocessing': 4,
        ...     'parsed_schema': {...}
        ... }
        >>> files = generate_files_parallel(params)
        >>> len(files)
        10
    """
    logger = get_logger()
    
    total_files = params['files_count']
    num_processes = params['multiprocessing']
    
    logger.info(f"Starting parallel generation: {total_files} file(s) with {num_processes} process(es)")
    
    # Distribute work across processes
    distribution = distribute_work(total_files, num_processes)
    
    # Prepare common parameters for all workers
    common_params = {
        'path': params['path'],
        'file_name': params['file_name'],
        'prefix_type': params['prefix_type'],
        'data_lines': params['data_lines'],
        'parsed_schema': params['parsed_schema']
    }
    
    # Prepare arguments for each worker
    worker_args = []
    current_index = 1
    
    for process_id in range(num_processes):
        files_for_this_process = distribution[process_id]
        
        # Skip if no files assigned to this process
        if files_for_this_process == 0:
            continue
        
        # Create parameters for this worker
        worker_params = common_params.copy()
        worker_params['start_index'] = current_index
        
        worker_args.append((process_id + 1, files_for_this_process, worker_params))
        
        # Update index for next process
        current_index += files_for_this_process
    
    # Create process pool and execute
    logger.debug(f"Creating process pool with {len(worker_args)} worker(s)")
    
    all_created_files = []
    
    with Pool(processes=num_processes) as pool:
        # Map worker function to all arguments
        results = pool.map(worker_function, worker_args)
        
        # Flatten results (list of lists -> single list)
        for result in results:
            all_created_files.extend(result)
    
    logger.info(f"Parallel generation completed: {len(all_created_files)} file(s) created")
    
    return all_created_files


def should_use_multiprocessing(files_count, multiprocessing):
    """
    Determine if multiprocessing should be used.
    
    Multiprocessing is beneficial when:
    - files_count > 1
    - multiprocessing > 1
    
    Args:
        files_count (int): Number of files to create
        multiprocessing (int): Number of processes configured
    
    Returns:
        bool: True if multiprocessing should be used
    
    Example:
        >>> should_use_multiprocessing(10, 4)
        True
        
        >>> should_use_multiprocessing(1, 4)
        False
        
        >>> should_use_multiprocessing(10, 1)
        False
    """
    return files_count > 1 and multiprocessing > 1
