import json
from pathlib import Path
import re
from tqdm import tqdm
from services.log_and_progress import *  # Update this import
from services.m3u_parser import sanitize_filename, remove_season_episode_info, remove_season_episode_info_full  # Update this import
import os


def create_json(entries, base_dir, folder_type):
    movies = []
    series = {}
    movie_count = 0
    series_count = 0

    base_dir_path = Path(base_dir)

    # Initialize the progress bar
    with tqdm(total=len(entries), desc=f"Writing JSON {folder_type}", unit="entry") as pbar:
        for entry in entries:
            if 'name' in entry and 'url' in entry:
                name = entry['name']
                title = entry.get('title', '')
                is_series = re.search(r'\b[Ss][._-]?\s*(\d{1,10})[._-]?\s*E\s*(\d{1,10})\b', name)

                if is_series or 'Series' in title:
                    
                    match = re.search(r'^(.*?)(?:\s*\[.*\])?\s*[Ss][._-]?\s*(\d{1,10})[._-]?\s*E(\d{1,10})$', name, re.IGNORECASE)
                    if match:
                        show_name, season, episode = match.groups()
                        season = season.zfill(2)
                        episode = episode.zfill(2)

                        # Sanitize and build episode info
                        safe_show_name = sanitize_filename(remove_season_episode_info(show_name))

                        # Define the series and season paths
                        series_path = base_dir_path / 'series' / safe_show_name
                        season_path = series_path / f"Season {season}"

                        # Initialize series data structure
                        if safe_show_name not in series:
                            series[safe_show_name] = {
                                'name': safe_show_name,
                                'path': str(series_path),
                                'image': None,
                                'seasons': {}
                            }

                        # Initialize season data structure if not already done
                        if season not in series[safe_show_name]['seasons']:
                            series[safe_show_name]['seasons'][season] = {
                                'path': str(season_path),
                                'episodes': []
                            }

                        # Build episode info
                        episode_info = {
                            'name': sanitize_filename(f"{safe_show_name} S{season} E{episode}"),
                            'logo': entry.get('logo'),
                            'url': entry.get('url', ''),
                            'path': str(season_path / f"{safe_show_name} S{season} E{episode}.strm"),
                            'season': season,
                            'episode': episode
                        }
                        series[safe_show_name]['seasons'][season]['episodes'].append(episode_info)

                        # Set the series image URL from the first episode of the first season (ignoring leading zeros)
                        if int(season) == 1 and int(episode) == 1:
                            if series[safe_show_name]['image'] is None:
                                series[safe_show_name]['image'] = entry.get('logo')

                        series_count += 1
                    elif is_series:
                        season, episode = is_series.groups()
                        show_name = entry['name']
                        season = season.zfill(2)
                        episode = episode.zfill(2)

                        # Sanitize and build episode info
                        safe_show_name = sanitize_filename(remove_season_episode_info_full(show_name))

                        # Define the series and season paths
                        series_path = base_dir_path / 'series' / safe_show_name
                        season_path = series_path / f"Season {season}"

                        # Initialize series data structure
                        if safe_show_name not in series:
                            series[safe_show_name] = {
                                'name': safe_show_name,
                                'path': str(series_path),
                                'image': None,
                                'seasons': {}
                            }

                        # Initialize season data structure if not already done
                        if season not in series[safe_show_name]['seasons']:
                            series[safe_show_name]['seasons'][season] = {
                                'path': str(season_path),
                                'episodes': []
                            }

                        # Build episode info
                        episode_info = {
                            'name': sanitize_filename(f"{safe_show_name} S{season} E{episode}"),
                            'logo': entry.get('logo'),
                            'url': entry.get('url', ''),
                            'path': str(season_path / f"{safe_show_name} S{season} E{episode}.strm"),
                            'season': season,
                            'episode': episode,
                            'duration': 'unkown',
                            'resolution': 'unkown'
                        }
                        series[safe_show_name]['seasons'][season]['episodes'].append(episode_info)

                        # Set the series image URL from the first episode of the first season (ignoring leading zeros)
                        if int(season) == 1 and int(episode) == 1:
                            if series[safe_show_name]['image'] is None:
                                series[safe_show_name]['image'] = entry.get('logo')

                        series_count += 1
                    else:
                        log_message('Could not parse series ' + entry['name'], level='error')
                        pass
                else:
                    safe_name = sanitize_filename(name)
                    dir_path = base_dir_path / 'movies' / safe_name
                    movie = {
                        'name': safe_name,
                        'logo': entry.get('logo'),
                        'url': entry.get('url', ''),
                        'path': str(dir_path),
                        'duration': 'Unknown',
                        'resolution': 'Unknown'
                    }
                    movies.append(movie)
                    movie_count += 1

            pbar.update(1)  # Update the progress bar after processing each entry

    # Write movies to JSON
    if folder_type == 'movies':
        file_path = base_dir_path / (folder_type + '.json')
        with open(file_path, 'w', encoding='utf-8') as movies_file:
            json.dump(movies, movies_file, ensure_ascii=False, indent=4)

    # Write series to JSON
    elif folder_type == 'series':
        file_path = base_dir_path / (folder_type + '.json')
        series_list = []
        for show_name, show_info in series.items():
            show_info['seasons'] = [
                {'season': season, **season_info}
                for season, season_info in show_info['seasons'].items()
            ]
            series_list.append(show_info)

        with open(file_path, 'w', encoding='utf-8') as series_file:
            json.dump(series_list, series_file, ensure_ascii=False, indent=4,)

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    

