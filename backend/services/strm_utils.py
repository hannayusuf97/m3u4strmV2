import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from services.log_and_progress import log_message  
from services.m3u_parser import sanitize_filename, remove_season_episode_info, remove_season_episode_info_full  # Update this import


def write_strm_file(entry, base_dir, file_type):
    if 'name' in entry and 'url' in entry:
        name = entry['name']
        title = entry.get('title', '')
        is_series = re.search(r'\b[Ss][._-]?\s*(\d{1,10})[._-]?\s*E\s*(\d{1,10})\b', name)

        if is_series or 'Series' in title:
            match = re.search(r'^(.*?)(?:\s*\[.*\])?\s*[Ss][._-]?\s*(\d{1,10})[._-]?\s*E(\d{1,10})$', name, re.IGNORECASE)
            
            if match:
                show_name, season, episode = match.groups()
                season = season.zfill(2)
                season_dir = f"Season {season}"
                safe_show_name = sanitize_filename(remove_season_episode_info(show_name))
                dir_path = os.path.join(base_dir, 'series', safe_show_name, season_dir)
                os.makedirs(dir_path, exist_ok=True)
                safe_name = sanitize_filename(f"{safe_show_name} S{season} E{episode}")
            
            
            elif is_series:
                season, episode = is_series.groups()
                show_name = entry['name']
                season = season.zfill(2)
                season_dir = f"Season {season}"
                safe_show_name = sanitize_filename(remove_season_episode_info_full(show_name))
                dir_path = os.path.join(base_dir, 'series', safe_show_name, season_dir)
                os.makedirs(dir_path, exist_ok=True)
                safe_name = sanitize_filename(f"{safe_show_name} S{season} E{episode}")
            
            else:
                log_message("Error couldn't parse " + entry['name'])
                return
        else:
            safe_name = sanitize_filename(name)
            dir_path = os.path.join(base_dir, 'movies', safe_name)
            os.makedirs(dir_path, exist_ok=True)
            safe_name = sanitize_filename(safe_name)

        file_name = safe_name + '.strm'
        file_path = os.path.join(dir_path, file_name)

        # Check if the .strm file already exists
        if os.path.exists(file_path):
            # Read the existing file content
            with open(file_path, 'r', encoding='utf-8') as existing_strm_file:
                existing_url = existing_strm_file.read().strip()

            # If the URL is the same, do not overwrite the file
            if existing_url == entry['url'].strip():
                return

        # Write or overwrite the .strm file with the new URL
        with open(file_path, 'w', encoding='utf-8') as strm_file:
            strm_file.write(entry['url'])


def write_strm_files(entries, base_dir, file_type, max_workers):
    total_entries = len(entries)

    with tqdm(total=total_entries, desc=f"Writing Streams {file_type}", unit="file") as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(write_strm_file, entry, base_dir, file_type) for entry in entries]
            for future in as_completed(futures):
                pbar.update(1)
