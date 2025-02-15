import os.path
from services.databases import *
from services.json_utils import load_json_file
from bson import ObjectId
from typing import Dict, Any, List
from services.media_stream import get_video_info
from services.log_and_progress import log_message
from services.json_utils import create_json
from services.m3u_parser import parse_m3u
from services.strm_utils import write_strm_files
import asyncio
import re
from pymongo.errors import PyMongoError

def serialize_basic_series(document):
    """Convert MongoDB document to a Series dict without seasons and episodes."""
    if '_id' in document:
        document['id'] = str(document['_id'])  # Convert ObjectId to string
    else:
        raise ValueError("Document is missing '_id' field.")

    # Exclude the 'seasons' field if present
    document.pop('seasons', None)

    return document


def serialize_series(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to a Series dict."""
    if '_id' in document:
        document['id'] = str(document['_id'])  # Convert ObjectId to string
    else:
        raise ValueError("Document is missing '_id' field.")

    # Iterate through seasons and episodes
    for season in document.get('seasons', []):
        if '_id' in season:
            season['id'] = str(season['_id'])
            del season['_id']
            del season['_id']

        for episode in season.get('episodes', []):
            if '_id' in episode:
                episode['id'] = str(episode['_id'])
                del episode['_id']
            else:
                episode['id'] = None

    return document


def serialize_movie(document):
    """Convert MongoDB document to a Movie dict."""
    document['id'] = str(document['_id'])  # Convert ObjectId to string
    return document


async def update_all_movies():
    async for movie in movies_collection.find():
        await update_movie_info(movie['_id'])


async def update_all_episodes():
    async for series in series_collection.find():
        for season in series['seasons']:
            for episode in season['episodes']:
                await update_episode_info(series['_id'], season['season'], episode['episode'])


async def delete_all_media_path_regex(provider_name: str):
    """
    Deletes documents where the `path` field starts with the given path,
    ensuring the path begins with 'results'.

    :param path: The path to use as a regex for deletion.
    :raises ValueError: If the path does not start with 'results'.
    :raises PyMongoError: If there is an error during the delete operation.
    """

    escaped_provider = re.escape(provider_name)

    # Construct a regex pattern to match paths containing both "results" and the provider name
    regex_pattern = f"results.*{escaped_provider}"

    # Define the query
    query = {"path": {"$regex": regex_pattern}}  # Case-insensitive matching

    try:
        # Perform the delete operations concurrently
        results = await asyncio.gather(
            movies_collection.delete_many(query),
            series_collection.delete_many(query),
        )

        # Log the results
        print(f"Deleted {results[0].deleted_count} entries from movies_collection.")
        print(f"Deleted {results[1].deleted_count} entries from series_collection.")

    except Exception as e:
        print(f"Error deleting entries: {e}")


async def insert_json_file(file_path: str, collection):
    """Insert a single JSON file into the specified MongoDB collection."""
    try:
        json_data = load_json_file(file_path)
        if isinstance(json_data, list):
            await collection.insert_many(json_data)
        else:
            await collection.insert_one(json_data)
    except Exception as e:
        print(f"Failed to insert data from {file_path}. Error: {e}")


async def insert_all_json_movies(file_paths: List[str]):
    for file_path in file_paths:
        print(f"Inserting movies JSON file: {file_path}")
        await insert_json_file(file_path, movies_collection)


async def insert_all_json_series(file_paths: List[str]):
    """Insert multiple JSON files into the MongoDB series collection."""
    for file_path in file_paths:
        print(f"Inserting series JSON file: {file_path}")
        await insert_json_file(file_path, series_collection)


async def find_series():
    series = []
    async for serie in series_collection.find():
        series.append(serialize_series(serie))
    return series


async def find_movies():
    movies = []
    async for movie in movies_collection.find():
        movies.append(serialize_movie(movie))
    return movies


async def find_movies_by_title(title: str) -> Dict[str, Any]:
    movie = await movies_collection.find_one({"name": title})
    return serialize_movie(movie) if movie else None


async def find_movies_by_id(movie_id: str) -> dict:
    """Find a movie by its string representation of ObjectId."""
    try:
        movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
        return serialize_movie(movie) if movie else None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


async def find_movies_by_url(url: str) -> Dict[str, Any]:
    movie = await movies_collection.find_one({"url": url})
    return serialize_movie(movie) if movie else None


async def find_series_by_name(name: str) -> List[Dict[str, Any]]:
    """Retrieve series by name from MongoDB and convert them to a list of dictionaries."""
    series = []
    async for doc in series_collection.find({"name": {"$regex": name, "$options": "i"}}):
        series.append(serialize_series(doc))
    return series


async def find_series_by_id(series_id: str) -> Dict[str, Any]:
    """Find a series by its ObjectId."""
    try:
        _id = ObjectId(series_id)
    except Exception:
        return None
    series = await series_collection.find_one({"_id": _id})
    return serialize_series(series) if series else None


async def find_season_by_series_id_and_season_number(series_id: str, season_number: str) -> Dict[str, Any]:
    """Find a season by series ID and season number with leading zeros."""
    formatted_season_number = season_number.zfill(2)  # Ensure two-digit format
    result = await series_collection.find_one(
        {'_id': ObjectId(series_id), 'seasons.season': formatted_season_number},
        {'_id': 0, 'seasons.$': 1}
    )
    return result


async def find_episode_by_series_id_season_and_episode_number(series_id: str, season_number: str,
                                                              episode_number: str) -> Dict[str, Any]:
    """Find an episode by series ID, season number, and episode number with leading zeros."""
    formatted_season_number = season_number.zfill(2)  # Ensure two-digit format
    formatted_episode_number = episode_number.zfill(2)  # Ensure two-digit format
    result = await series_collection.find_one(
        {'_id': ObjectId(series_id), 'seasons.season': formatted_season_number,
         'seasons.episodes.episode': formatted_episode_number},
        {'_id': 0, 'seasons.$': 1}
    )
    return result


async def update_movie_info(movie_id: str):
    """
    Fetch movie info, get video details, and update the movie record in the database.
    
    Args:
        movie_id (str): The string representation of the movie's ObjectId.
    """
    try:
        # Fetch the movie data by ID
        print(f"Attempting to fetch movie data for ID: {movie_id}")
        movie_data = await find_movies_by_id(movie_id)
        if not movie_data:
            print(f"No movie found with ID: {movie_id}")
            return

        # Extract the movie URL
        movie_url = movie_data.get('url')
        print(f"Movie URL: {movie_url}")

        if not movie_url:
            print(f"No URL found for movie ID: {movie_id}")
            return

        # Get video info (duration and resolution)
        print(f"Fetching video info for URL: {movie_url}")
        duration, resolution = get_video_info(movie_url)
        print(f"Video info retrieved - Duration: {duration}, Resolution: {resolution}")

        if duration is None or resolution is None:
            print(f"Failed to retrieve video info for URL: {movie_url}")
            return

        # Update the movie document in MongoDB
        update_result = await movies_collection.update_one(
            {"_id": ObjectId(movie_id)},
            {"$set": {"duration": duration, "resolution": resolution}}
        )

        # Print the movie updates for resolution and duration
        if update_result.modified_count > 0:
            print(f"Movie updated: Resolution: {resolution}, Duration: {duration}")
        else:
            print(f"No changes made for movie ID: {movie_id} {resolution} {duration}")

    except Exception as e:
        print(f"An error occurred while updating movie info: {e}")


async def update_episode_info(series_id: str, season_number: str, episode_number: str):
    """Fetch episode info, get video details, and update the episode record in the database."""
    episode_data = await find_episode_by_series_id_season_and_episode_number(series_id, season_number, episode_number)
    if episode_data:
        episode = episode_data['seasons'][0]['episodes'][0]
        duration, resolution = get_video_info(episode['url'])
        episode['duration'] = duration
        episode['quality'] = resolution
        await series_collection.update_one(
            {
                "_id": ObjectId(series_id),
                "seasons.season": season_number.zfill(2),
                "seasons.episodes.episode": episode_number.zfill(2)
            },
            {
                "$set": {
                    "seasons.$.episodes.$[ep].duration": duration,
                    "seasons.$.episodes.$[ep].quality": resolution
                }
            },
            array_filters=[{"ep.episode": episode_number.zfill(2)}]
        )


async def update_series_info(series_id: str, duration: str, resolution: str):
    """
    Update the series record with duration and resolution information.
    
    Args:
        series_id (str): The string representation of the series' ObjectId
        duration (str): The duration of the series
        resolution (str): The resolution of the series
    """
    try:
        # Convert string ID to ObjectId
        _id = ObjectId(series_id)

        # Update the series document in MongoDB
        update_result = await series_collection.update_one(
            {"_id": _id},
            {"$set": {
                "duration": duration,
                "resolution": resolution
            }}
        )

        if update_result.modified_count > 0:
            print(f"Series updated successfully - ID: {series_id}, Resolution: {resolution}, Duration: {duration}")
        else:
            print(f"No changes made for series ID: {series_id} (Document might not exist or values unchanged)")

    except Exception as e:
        print(f"An error occurred while updating series info: {e}")
        raise


# async def load_m3u(m3u_files):
#     for m3u_file in m3u_files:
#         m3u_file = os.path.normpath(m3u_file)
#         try:
#             base_name = os.path.basename(m3u_file).split('.m3u')[0]
#             output_dir = f'./results/Result_{base_name}'
#             log_message(f"Processing m3u File: {m3u_file}", level='info')

#             movies, series = parse_m3u(m3u_file)
#             max_workers = max(1, os.cpu_count() - 2)
#             write_strm_files(movies, output_dir, 'movies', max_workers)
#             write_strm_files(series, output_dir, 'series', max_workers)
#             if not os.path.exists(output_dir):
#                 os.makedirs(output_dir)

#             create_json(movies, output_dir, 'movies')
#             print('Movies JSON created successfully')
#             create_json(series, output_dir, 'series')
#             print('Series JSON created successfully')

#             movies_json_path = os.path.normpath(os.path.join(output_dir, 'movies.json'))
            
#             series_json_path = os.path.normpath(os.path.join(output_dir, 'series.json'))
#             if os.path.exists(movies_json_path):
#                 print(f"Found movies JSON file: {movies_json_path}")
#             else:
#                 print(f"Movies JSON file not found in {output_dir}")

#             if os.path.exists(series_json_path):

#                 print(f"Found series JSON file: {series_json_path}")
#             else:
#                 print(f"Series JSON file not found in {output_dir}")

#             # Insert all found movies JSON files
#             print(f"Inserting movies JSON file: {movies_json_path}")
#             await insert_all_json_movies([movies_json_path])
#             # Insert all found series JSON files
#             print(f"Inserting series JSON file: {series_json_path}")
#             await insert_all_json_series([series_json_path])
#             log_message(f"Processing completed for: {m3u_file}", level='info')
#         except Exception as e:
#             log_message(f"Error processing {m3u_file}: {str(e)}", level='error')
