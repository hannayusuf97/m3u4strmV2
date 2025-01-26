import os
import asyncio
import argparse
from services.database_service import insert_all_json_movies, insert_all_json_series
from services.json_utils import create_json
from services.log_and_progress import log_message
from services.m3u_parser import parse_m3u
from services.strm_utils import write_strm_files
import uvicorn


def create_results(m3u_files):
    for m3u_file in m3u_files:
        try:
            base_name = os.path.basename(m3u_file).split('.')[0]
            output_dir = f'./results/Result_{base_name}'
            log_message(f"Processing m3u File: {m3u_file}", level='info')

            movies, series = parse_m3u(m3u_file)
            max_workers = max(1, os.cpu_count() - 2)
            write_strm_files(movies, output_dir, 'movies', max_workers)
            write_strm_files(series, output_dir, 'series', max_workers)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            log_message(f"Processing completed for: {m3u_file}", level='info')
        except Exception as e:
            log_message(f"Error processing {m3u_file}: {str(e)}", level='error')


def create_json_files(m3u_files):
    for m3u_file in m3u_files:
        try:
            base_name = os.path.basename(m3u_file).split('.')[0]
            output_dir = f'./results/Result_{base_name}'
            log_message(f"Processing m3u File: {m3u_file}", level='info')
            movies, series = parse_m3u(m3u_file)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            create_json(movies, output_dir, 'movies')
            log_message(f"Movie processing completed for: {m3u_file}", level='info')
            create_json(series, output_dir, 'series')
            log_message(f"Series processing completed for: {m3u_file}", level='info')
        except Exception as e:
            log_message(f"Error processing {m3u_file}: {str(e)}", level='error')


async def insert_all_m3us():
    base_directory = r"./results"
    movies_json_paths = []
    series_json_paths = []

    for subdir in os.listdir(base_directory):
        subdir_path = os.path.join(base_directory, subdir)
        if os.path.isdir(subdir_path):
            movies_json_path = os.path.join(subdir_path, "movies.json")
            series_json_path = os.path.join(subdir_path, "series.json")

            if os.path.exists(movies_json_path):
                movies_json_paths.append(movies_json_path)
                print(f"Found movies JSON file: {movies_json_path}")
            else:
                print(f"Movies JSON file not found in {subdir_path}")

            if os.path.exists(series_json_path):
                series_json_paths.append(series_json_path)
                print(f"Found series JSON file: {series_json_path}")
            else:
                print(f"Series JSON file not found in {subdir_path}")

    for movie_path in movies_json_paths:
        await insert_all_json_movies([movie_path])

    for series_path in series_json_paths:
        await insert_all_json_series([series_path])


async def insert_a_single_file_to_database(m3u_file_path):
    movies_json_path = os.path.join(m3u_file_path, "movies.json")
    series_json_path = os.path.join(m3u_file_path, "series.json")

    if os.path.exists(movies_json_path):
        print(f"Found movies JSON file: {movies_json_path}")
        await insert_all_json_movies([movies_json_path])
    else:
        print(f"Movies JSON file not found at: {movies_json_path}")

    if os.path.exists(series_json_path):
        print(f"Found series JSON file: {series_json_path}")
        await insert_all_json_series([series_json_path])
    else:
        print(f"Series JSON file not found at: {series_json_path}")


def main():
    parser = argparse.ArgumentParser(description="Utility script for handling M3U files and JSON processing.")
    parser.add_argument('command', choices=['create_results', 'create_json_files', 'insert_all_m3us', 'insert_single'],
                        help="The command to run.")
    parser.add_argument('m3u_files', nargs='*', help="List of M3U file paths to process.")
    parser.add_argument('path', help="Path to a single directory for database insertion (only for 'insert_single').")

    args = parser.parse_args()

    if args.command == 'create_results':
        if not args.m3u_files:
            print("Error: No M3U files provided.")
        else:
            create_results(args.m3u_files)

    elif args.command == 'create_json_files':
        if not args.m3u_files:
            print("Error: No M3U files provided.")
        else:
            create_json_files(args.m3u_files)

    elif args.command == 'insert_all_m3us':
        asyncio.run(insert_all_m3us())

    elif args.command == 'insert_single':
        if not args.path:
            print("Error: No path provided for single file insertion.")
        else:
            asyncio.run(insert_a_single_file_to_database(args.path))


if __name__ == "__main__":
    main()
