import shutil
import threading

from models.provider_model import Provider
from services.database_service import *
import os
import asyncio
from urllib.parse import urlsplit
from fastapi import FastAPI, WebSocket, BackgroundTasks, WebSocket
from concurrent.futures import ThreadPoolExecutor, wait

app = FastAPI()

# Thread pool for running blocking tasks in the background
executor = ThreadPoolExecutor()

# Global variable to keep track of the total items to delete
total_items_to_delete = 0
deleted_items_count = 0

async def get_provider_names_and_paths():
    results_directory = os.path.normpath(os.path.join(os.getcwd(), 'results'))
    if not os.path.exists(results_directory):
        return "Error: Results directory does not exist"
    else:
        try:
            provider_paths = [ f.path for f in os.scandir(results_directory) if f.is_dir() ]
            provider_names = [os.path.basename(path) for path in provider_paths]
            return list(zip(provider_names, provider_paths))
        except Exception as e:
            return f"An error occurred: {str(e)}"

### reconsider checking for series too
async def get_provider_data():
    data = await get_provider_names_and_paths()
    if isinstance(data, str):
        print(data)
        return []
    provider_data = []
    for provider_name, path in data:
        try:
            movies_file = os.path.join(path, 'movies.json')
            series_file = os.path.join(path, 'series.json')
            if os.path.exists(movies_file):
                movies = load_json_file(movies_file)
                if movies and 'url' in movies[0]:
                    url = movies[0]['url']
                    split_url = urlsplit(url)
                    provider_url = split_url._replace(path="", query="", fragment="").geturl()
                    url_path_components = split_url.path.strip("/").split("/")
                    provider_username = url_path_components[-3] if len(url_path_components) > 1 else None
                    provider_password = url_path_components[-2] if len(url_path_components) > 1 else None

                    # Pass valid inputs to Provider
                    new_provider = Provider(
                        name=str(provider_name),
                        path=str(path),
                        username=str(provider_username),
                        password=str(provider_password),
                        link=str(provider_url)
                    )
                    provider_data.append(new_provider)
                else:
                    if os.path.exists(series_file):
                        series = load_json_file(series_file)
                        if series and 'url' in series[0]['seasons'][0]['episodes'][0]:
                            url = series[0]['seasons'][0]['episodes'][0]['url']
                            split_url = urlsplit(url)
                            provider_url = split_url._replace(path="", query="", fragment="").geturl()
                            url_path_components = split_url.path.strip("/").split("/")
                            provider_username = url_path_components[-3] if len(url_path_components) > 1 else None
                            provider_password = url_path_components[-2] if len(url_path_components) > 1 else None

                            # Pass valid inputs to Provider
                            new_provider = Provider(
                                name=str(provider_name),
                                path=str(path),
                                username=str(provider_username),
                                password=str(provider_password),
                                link=str(provider_url)
                            )
                            provider_data.append(new_provider)
        except Exception as e:
            print(f"An error occurred with {provider_name}: {str(e)}")
            continue
    return provider_data


async def delete_all_providers(providers: List[Provider]) -> List[str]:
    """Delete providers based on their name and path."""
    deleted_paths = []
    try:
        for provider in providers:
            # Use provider.name for regex-based deletion in the database
            await delete_all_media_path_regex(provider.name)
            deleted_paths.append(provider.path)
        return deleted_paths
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise  # Re-raise the exception to be handled by the API endpoint


async def delete_files_and_folders(provider_path: str, websocket: WebSocket):
    global total_items_to_delete, deleted_items_count
    total_items_to_delete = 0
    deleted_items_count = 0

    # Count total files and folders
    for root, dirs, files in os.walk(provider_path):
        total_items_to_delete += len(files) + len(dirs)

    # Delete files and folders
    for root, dirs, files in os.walk(provider_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)
            deleted_items_count += 1
            await websocket.send_json({"type": "progress"})  # Send progress update

        for name in dirs:
            dir_path = os.path.join(root, name)
            shutil.rmtree(dir_path)
            deleted_items_count += 1
            await websocket.send_json({"type": "progress"})  # Send progress update

    await websocket.send_json({"type": "completed"})  # Notify completion
