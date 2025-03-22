#!/usr/bin/env python3
"""
Plex NFO Creator - Creates NFO files with IMDb/TMDb/TVDB links from Plex metadata

Usage: python plex_nfo_creator.py --token TOKEN --root-path PATH [options]
"""

import os
import sys
import re
import logging
import argparse
import platform
from tqdm import tqdm
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound

# Configure logging
def setup_logging():
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plex_nfo_creator.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='Create NFO files from Plex metadata')
    parser.add_argument('--url', default='http://localhost:32400', help='Plex server URL')
    parser.add_argument('--token', required=True, help='Plex authentication token')
    parser.add_argument('--library', default='Movies', help='Plex library name')
    parser.add_argument('--type', default='movie', choices=['movie', 'tv'], help='Library type: movie or tv')
    parser.add_argument('--root-path', required=True, help='Root path of the media library')
    parser.add_argument('--dry-run', action='store_true', help='Simulate operations without writing files')
    return parser.parse_args()

def connect_to_plex(url, token):
    try:
        logger.info(f"Connecting to Plex server at {url}")
        return PlexServer(url, token)
    except Exception as e:
        logger.error(f"Failed to connect to Plex server: {e}")
        sys.exit(1)

def get_ids(item, item_type):
    ids = {'imdb': None, 'tmdb': None, 'tvdb': None}
    method_used = "primary"
    
    try:
        # Method 1: Extract from guids
        for guid in item.guids:
            guid_id = guid.id.lower()
            if 'imdb' in guid_id:
                ids['imdb'] = guid_id.split('//')[1]
            elif 'tmdb' in guid_id and item_type == 'movie':
                ids['tmdb'] = guid_id.split('//')[1]
            elif 'tvdb' in guid_id and item_type == 'tv':
                ids['tvdb'] = guid_id.split('//')[1]
        
        # Method 2: Extract from other metadata if needed
        if not (ids['imdb'] or (ids['tmdb'] and item_type == 'movie') or (ids['tvdb'] and item_type == 'tv')):
            method_used = "secondary"
            if hasattr(item, 'fields'):
                for field in item.fields:
                    if field.name == 'guid':
                        value = field.value.lower()
                        if not ids['imdb']:
                            imdb_match = re.search(r'(tt\d+)', value)
                            if imdb_match:
                                ids['imdb'] = imdb_match.group(1)
                        
                        if not ids['tmdb'] and item_type == 'movie':
                            tmdb_match = re.search(r'tmdb://(\d+)', value)
                            if tmdb_match:
                                ids['tmdb'] = tmdb_match.group(1)
                        
                        if not ids['tvdb'] and item_type == 'tv':
                            tvdb_match = re.search(r'tvdb://(\d+)', value)
                            if tvdb_match:
                                ids['tvdb'] = tvdb_match.group(1)
        
        return ids, method_used
    except Exception as e:
        logger.error(f"Error extracting IDs for {item.title}: {e}")
        return ids, method_used

def normalize_path(path):
    """Normalize path for the current operating system."""
    path = os.path.abspath(path)
    
    if platform.system() == 'Windows':
        # Just normalize path separators, but preserve case
        path = os.path.normpath(path)
    else:
        path = os.path.normpath(path)
    
    return path

def get_local_path(plex_path, root_path, item_type):
    """Convert Plex path to local filesystem path using the provided root path."""
    # Normalize paths without changing case
    plex_path = normalize_path(plex_path)
    root_path = normalize_path(root_path)
    
    # Handle drive letter mapping (e.g., C:\filme to Y:\filme)
    if platform.system() == 'Windows':
        # Extract the drive letters, but don't change case for the full paths
        plex_drive_letter = os.path.splitdrive(plex_path)[0]
        root_drive_letter = os.path.splitdrive(root_path)[0]
        
        # For comparison only, use lowercase
        if plex_drive_letter.lower() != root_drive_letter.lower():
            # Get the path without the drive letter
            plex_path_no_drive = os.path.splitdrive(plex_path)[1]
            # Combine the root drive with the path
            mapped_path = os.path.join(root_drive_letter, plex_path_no_drive)
            logger.debug(f"Mapped drive {plex_drive_letter} to {root_drive_letter}: {mapped_path}")
            return mapped_path
    
    # For movies, extract the movie folder and filename
    if item_type == 'movie':
        movie_folder = os.path.basename(os.path.dirname(plex_path))
        movie_filename = os.path.basename(plex_path)
        
        # Search for the movie folder in the root path
        for root, dirs, _ in os.walk(root_path):
            # On Windows, do case-insensitive comparison
            if platform.system() == 'Windows':
                if any(d.lower() == movie_folder.lower() for d in dirs):
                    # Find the actual directory name with preserved case
                    actual_folder = next(d for d in dirs if d.lower() == movie_folder.lower())
                    folder_path = os.path.join(root, actual_folder)
                    
                    # Look for the file in this folder
                    if os.path.exists(os.path.join(folder_path, movie_filename)):
                        return os.path.join(folder_path, movie_filename)
                    
                    # If exact match not found, try case-insensitive search for the file
                    for file in os.listdir(folder_path):
                        if file.lower() == movie_filename.lower():
                            return os.path.join(folder_path, file)
            else:
                # On Linux/Mac, do case-sensitive comparison
                if movie_folder in dirs:
                    potential_path = os.path.join(root, movie_folder, movie_filename)
                    if os.path.exists(potential_path):
                        return potential_path
    
    # For TV shows, find the show folder
    else:
        show_name = os.path.basename(plex_path)
        
        # Search for the directory in the root path
        for root, dirs, _ in os.walk(root_path):
            # On Windows, do case-insensitive comparison
            if platform.system() == 'Windows':
                for dir_name in dirs:
                    if dir_name.lower() == show_name.lower():
                        return os.path.join(root, dir_name)
            else:
                # On Linux/Mac, do case-sensitive comparison
                if show_name in dirs:
                    return os.path.join(root, show_name)
    
    # If we can't find a match, try a simple drive letter replacement
    if platform.system() == 'Windows':
        # Replace the drive letter but preserve case of the path
        root_drive = os.path.splitdrive(root_path)[0]
        path_without_drive = os.path.splitdrive(plex_path)[1]
        mapped_path = root_drive + path_without_drive
        
        # Check if this path exists
        if os.path.exists(mapped_path):
            logger.info(f"Found path by drive letter replacement: {mapped_path}")
            return mapped_path
    
    # If we can't find a match, log a warning and return the original path
    logger.warning(f"Could not find {plex_path} under {root_path}")
    return plex_path

def create_nfo_file(plex_path, ids, item_type, root_path, dry_run=False):
    try:
        # Get the appropriate local path
        local_path = get_local_path(plex_path, root_path, item_type)
        
        # Verify the path exists
        if not os.path.exists(local_path):
            logger.error(f"Path does not exist: {local_path}")
            return False
        
        # For TV shows, create tvshow.nfo in the show folder
        if item_type == 'tv':
            if not os.path.isdir(local_path):
                logger.error(f"TV show path is not a directory: {local_path}")
                return False
            
            nfo_path = os.path.join(local_path, "tvshow.nfo")
            
            # Check write permissions
            if not os.access(local_path, os.W_OK):
                logger.error(f"Cannot write to directory: {local_path}")
                return False
            
            # Create content with available IDs
            if ids['imdb']:
                content = f"https://www.imdb.com/title/{ids['imdb']}/"
            elif ids['tvdb']:
                content = f"https://thetvdb.com/series/{ids['tvdb']}"
            else:
                logger.warning(f"No valid ID found for TV show at {local_path}")
                return False
        
        # For movies, create .nfo file next to the movie file
        else:
            if not os.path.isfile(local_path):
                logger.error(f"Movie path is not a file: {local_path}")
                return False
            
            movie_dir = os.path.dirname(local_path)
            movie_filename = os.path.splitext(os.path.basename(local_path))[0]
            nfo_path = os.path.join(movie_dir, f"{movie_filename}.nfo")
            
            # Check write permissions
            if not os.access(movie_dir, os.W_OK):
                logger.error(f"Cannot write to directory: {movie_dir}")
                return False
            
            # Create content with available IDs
            if ids['imdb']:
                content = f"https://www.imdb.com/title/{ids['imdb']}/"
            elif ids['tmdb']:
                content = f"https://www.themoviedb.org/movie/{ids['tmdb']}"
            else:
                logger.warning(f"No valid ID found for movie at {local_path}")
                return False
        
        # Handle dry run
        if dry_run:
            logger.info(f"[DRY RUN] Would create NFO file at: {nfo_path}")
            return True
        
        # Write the NFO file
        with open(nfo_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Created NFO file at: {nfo_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create NFO file for {plex_path}: {e}")
        return False

def process_library(plex, library_name, library_type, root_path, dry_run=False):

    try:
        # Get the library section
        section = plex.library.section(library_name)
        items = section.all()
        
        logger.info(f"Processing {len(items)} items in {library_type} library '{library_name}'")
        logger.info(f"Using root path: {root_path}")
        
        # Verify root path exists
        if not os.path.isdir(root_path):
            logger.error(f"Root path is not a valid directory: {root_path}")
            sys.exit(1)
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        primary_count = 0
        secondary_count = 0
        
        # Process items with progress bar
        item_type = "movies" if library_type == "movie" else "TV shows"
        for item in tqdm(items, desc=f"Processing {item_type}", unit="item"):
            logger.info(f"Processing {library_type}: {item.title}")
            
            # Skip items without locations
            if not item.locations or len(item.locations) == 0:
                logger.warning(f"Skipping {item.title}: No location found")
                skipped_count += 1
                continue
            
            item_path = item.locations[0]
            
            # Get IDs
            ids, method = get_ids(item, library_type)
            
            # Track method used
            if method == "primary":
                primary_count += 1
            else:
                secondary_count += 1
            
            # Create NFO file if we have at least one ID
            has_id = ids['imdb'] or (ids['tmdb'] and library_type == 'movie') or (ids['tvdb'] and library_type == 'tv')
            if has_id:
                if create_nfo_file(item_path, ids, library_type, root_path, dry_run):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                logger.warning(f"No IDs found for {item.title}")
                failed_count += 1
        
        # Log results
        logger.info(f"Completed processing {len(items)} {item_type}")
        logger.info(f"Success: {success_count}, Failed: {failed_count}, Skipped: {skipped_count}")
        logger.info(f"IDs found using primary method: {primary_count}")
        logger.info(f"IDs found using secondary method: {secondary_count}")
        
    except NotFound:
        logger.error(f"Library '{library_name}' not found on Plex server")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred while processing {library_type} library: {e}")
        sys.exit(1)

def main():
    args = parse_args()
    
    global logger
    logger = setup_logging()
    
    logger.info("Starting Plex NFO Creator")
    
    # Connect to Plex server
    plex = connect_to_plex(args.url, args.token)
    
    # Process library
    process_library(plex, args.library, args.type, args.root_path, args.dry_run)
    
    logger.info("Plex NFO Creator completed")

if __name__ == "__main__":
    main()