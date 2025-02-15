import uuid
from typing import List, Union, Dict
from fastapi import HTTPException, APIRouter, Query, File, UploadFile, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from models.media_models import Movie, Series, Season, Episode, MediaItem
from services.media_stream import get_video_info
from services.database_service import (
    movies_collection,
    series_collection,  # Make sure to import series_collection if using Motor
    serialize_movie,
    serialize_series,
    find_series_by_id,
    find_movies_by_id,
    find_season_by_series_id_and_season_number,
    find_episode_by_series_id_season_and_episode_number,
    serialize_basic_series,
    update_movie_info,
    update_series_info,
    insert_all_json_movies,
    insert_all_json_series
)
from threading import Lock
from models.provider_model import Provider
from bson import ObjectId
from services.copy_files import copy_movie, copy_series, copy_season, copy_episode
from pydantic import ValidationError, BaseModel
from dotenv import load_dotenv
import os
from datetime import datetime
from services.provider_service import get_provider_data, delete_all_providers
from services.jellyfin_auth import scanLibrary,getisAdmin
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
import uuid
from services.log_and_progress import progress_tracker
from services.json_utils import create_json
from services.m3u_parser import parse_m3u
from services.strm_utils import write_strm_files
import asyncio
import jwt


router = APIRouter()
# Load environment variables from .env file
load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
secret_key = os.environ.get('SECRET_TOKEN') 
algorithm = os.environ.get('ALGORITHM', 'H256')
access_token_expire_minutes = 30
refresh_token_expire_days = 7 
server_url = os.environ.get('JELLYFIN_URL')

# Get the admin password from environment variables (this should be the hashed password)
# Ensure this is the hashed password
class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    """Login endpoint to authenticate user."""
    try:
        hashed_admin_password = os.getenv("ADMIN_PASSWORD")
        # Compare the input password with the hashed password
        if request.password == hashed_admin_password:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/media_info/{url:path}", response_model=dict)
async def get_media_info(url: str, media_id: str, media_type: str):
    """Get video information such as duration and resolution for movies or series."""
    duration, resolution = get_video_info(url)

    if media_type == "movie":
        await update_movie_info(media_id)
    elif media_type == "series":
        await update_series_info(media_id, duration, resolution)
    else:
        raise HTTPException(status_code=400, detail="Invalid media type")

    return {
        "id": media_id,
        "duration": duration,
        "resolution": resolution
    }


@router.get("/series/basic/", response_model=List[Series])
async def get_basic_series_info(page: int = Query(1, ge=1), size: int = Query(50, le=100)):
    skip = (page - 1) * size
    # Exclude the 'seasons' field
    series_cursor = series_collection.find({}, {'seasons': 0}).skip(skip).limit(size)
    series_list = []

    async for series in series_cursor:
        # Serialize series without seasons
        series_dict = serialize_basic_series(series)
        series_list.append(Series(**series_dict))

    return series_list


@router.get("/series/{series_id}", response_model=Series)
async def get_series_by_id(series_id: str) -> Series:
    try:
        _id = ObjectId(series_id)  # Ensure the ID is valid
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid series ID format")

    series = await find_series_by_id(_id)  # Fetch series from the database

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    return serialize_series(series)  # Return the series as JSON


@router.get("/movies/{movie_id}", response_model=Movie)
async def get_movie_by_id(movie_id: str) -> Movie:
    """Retrieve a movie by its ID from MongoDB."""
    try:
        _id = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid movie ID format")

    movie = await find_movies_by_id(_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return serialize_movie(movie)


@router.get("/series/{series_id}/seasons/{season_number}", response_model=Season)
async def get_season(series_id: str, season_number: str) -> Season:
    """Retrieve a specific season by series ID and season number."""
    season_doc = await find_season_by_series_id_and_season_number(series_id, season_number)
    if not season_doc:
        raise HTTPException(status_code=404, detail="Season not found")
    return season_doc['seasons'][0]


@router.get("/series/{series_id}/seasons/{season_number}/episodes/{episode_number}", response_model=Episode)
async def get_episode(series_id: str, season_number: str, episode_number: str) -> Episode:
    """Retrieve a specific episode by series ID, season number, and episode number."""
    series_doc = await find_episode_by_series_id_season_and_episode_number(series_id, season_number, episode_number)
    if not series_doc or not series_doc['seasons']:
        raise HTTPException(status_code=404, detail="Episode not found")
    for season in series_doc['seasons']:
        for episode in season['episodes']:
            if episode['episode'] == episode_number.zfill(2):
                return episode
    raise HTTPException(status_code=404, detail="Episode not found")


@router.get("/series/", response_model=List[Series])
async def get_all_series(page: int = Query(1, ge=1), size: int = Query(50, le=100)):
    skip = (page - 1) * size
    series_cursor = series_collection.find().skip(skip).limit(size)
    series_list = []

    async for series in series_cursor:
        series_dict = serialize_series(series)
        series_list.append(Series(**series_dict))

    return series_list


@router.get("/media/", response_model=List[Union[Movie, Series]])
async def get_all_media(page: int = Query(1, ge=1), size: int = Query(50, le=100)):
    skip = (page - 1) * size

    # Retrieve movies and series
    movies_cursor = movies_collection.find().skip(skip).limit(size)
    series_cursor = series_collection.find().skip(skip).limit(size)

    # Combine results
    media_items = []

    # Process movies
    async for movie in movies_cursor:
        movie_dict = serialize_movie(movie)
        media_items.append(Movie(**movie_dict))

    # Process series
    async for series in series_cursor:
        series_dict = serialize_series(series)
        media_items.append(Series(**series_dict))

    return media_items


@router.get("/movies/", response_model=List[Movie])
async def get_all_movies(page: int = Query(1, ge=1), size: int = Query(50, le=100)):
    skip = (page - 1) * size
    movies_cursor = movies_collection.find().skip(skip).limit(size)
    movies_list = []

    async for movie in movies_cursor:
        movie_dict = serialize_movie(movie)
        movies_list.append(Movie(**movie_dict))

    return movies_list


@router.get("/search/", response_model=List[Union[Movie, Series]])
async def search(query: str, page: int = Query(1, ge=1), size: int = Query(50, le=100)):
    """Search for movies and series by a query string with pagination."""
    skip = (page - 1) * size

    print(movies_collection)
    # Search for movies with limit and skip
    movie_cursor = movies_collection.find({"name": {"$regex": query, "$options": "i"}}).skip(skip).limit(size)
    movies = [serialize_movie(doc) async for doc in movie_cursor]
    print(f"Movies List Length: {len(movies)}")  # Debugging

    # Search for series with limit and skip
    series_cursor = series_collection.find({"name": {"$regex": query, "$options": "i"}}).skip(skip).limit(size)
    series_list = [serialize_series(doc) async for doc in series_cursor]
    print(f"Series List Length: {len(series_list)}")  # Debugging

    # Combine results and handle pagination
    combined_results = movies + series_list
    return combined_results


@router.post("/watchlist/", response_model=dict)
async def receive_watchlist(watchlist: List[MediaItem]):
    """Receive a watchlist from the frontend."""
    try:
        for item in watchlist:
            print(f"Received item: {item}")  # Log the raw item data

            if isinstance(item, Movie):
                try:
                    print(f"Received movie: {item.name} {item.path}")  # Debugging log
                    copy_movie(item.path)

                except ValidationError as ve:
                    print(f"Validation error: {ve}")  # Log the validation error
                    raise HTTPException(status_code=400, detail=str(ve))

            elif item.type == 'Series':
                try:
                    print(f"Received series: {item.name} {item.path}")  # Debugging log
                    copy_series(item.path)

                except ValidationError as ve:
                    print(f"Validation error: {ve}")  # Log the validation error
                    raise HTTPException(status_code=400, detail=str(ve))

            elif item.type == 'Episode':
                print(f"Raw episode data: {item}")  # Debugging log
                try:
                    episode_item = Episode(**item.model_dump())  # Instantiate Episode model
                    print(
                        f"Received episode: {episode_item.name} {episode_item.path} {episode_item.season} ")  # Debugging log
                    copy_episode(episode_item.path)
                    # Print all attributes of the episode_item
                except ValidationError as ve:
                    print(f"Validation error: {ve}")  # Log the validation error
                    raise HTTPException(status_code=400, detail=str(ve))

            elif item.type == 'Season':
                try:
                    season_item = Season(**item.model_dump())  # Instantiate Season model
                    print(f"Received season: {season_item.path} Type: {season_item.type}")  # Debugging log
                    copy_season(season_item.path)

                except ValidationError as ve:
                    print(f"Validation error: {ve}")  # Log the validation error
                    raise HTTPException(status_code=400, detail=str(ve))
            else:
                print(f"Received unknown item type: {type(item)}")  # Debugging log
                raise HTTPException(status_code=400, detail="Invalid media item type")
        scanLibrary()
        return {"message": "Watchlist received successfully!"}

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error message
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series_info/{url:path}", response_model=dict)
async def get_series_info(url: str, s_id: str):
    """Get video information such as duration and resolution for series."""
    duration, resolution = get_video_info(url)

    # Update the series with the new information
    await update_series_info(s_id, duration, resolution)

    return {
        "id": s_id,
        "duration": duration,
        "resolution": resolution
    }

# Admin stuff


async def admin_required(token: str = Depends(oauth2_scheme)):
    # First get the username from the token
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Now check if the user is admin using the username
        if not getisAdmin(username):
            raise HTTPException(status_code=403, detail="Admin access required")
            
        return username
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
@router.get("/m3us", response_model=dict, dependencies=[Depends(admin_required)])
async def get_m3us():

    file_info = {}
    folder_path = './m3us'
    # Iterate through the files in the folder
    for file_name in os.listdir(folder_path):
        # Check if the file ends with .m3u or .m3u8
        if file_name.endswith(('.m3u', '.m3u8')):
            file_path = os.path.join(folder_path, file_name)
            creation_time = os.path.getctime(file_path)  # Get the creation time of the file
            creation_date = datetime.fromtimestamp(creation_time).strftime(
                '%Y-%m-%d %H:%M:%S')  # Convert to a readable format

            # Add file information to the dictionary
            file_info[file_name] = {
                'file_path': os.path.normpath(file_path),  # Normalize the file path
                'creation_date': creation_date
            }
    return file_info  # Return as a dictionary


@router.post("/delete-m3us", dependencies=[Depends(admin_required)])
async def delete_m3us(m3us: List[dict]):
    """Delete selected M3U files."""

    try:
        for m3u in m3us:
            file_path = m3u.get("filePath")

            # Check if the file exists before attempting to delete
            if os.path.exists(file_path) and (file_path.endswith(".m3u") or file_path.endswith(".m3u8")):
                os.remove(file_path)  # Delete the file
            else:
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        return {"message": "M3Us deleted successfully!"}
    except Exception as e:
        print(f"Error during deletion: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/upload-m3u", dependencies=[Depends(admin_required)])
async def upload_m3u(files: List[UploadFile] = File(...)):

    """Upload new M3U files."""
    uploaded_files = []
    upload_directory = './m3us'  # Ensure this directory exists
    if not os.path.isdir(upload_directory):
        raise FileNotFoundError(f"The directory '{upload_directory}' does not exist.")

    for file in files:
        if file.filename.endswith('.m3u') or file.filename.endswith('.m3u8'):
            file_location = os.path.join(upload_directory, file.filename)
            with open(file_location, "wb") as f:
                f.write(await file.read())
            uploaded_files.append({
                "file": file.filename,
                "path": os.path.normpath(file_location),
                "creation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add creation time
            })

    return uploaded_files



security = HTTPBearer()



@router.post('/load-m3u', dependencies=[Depends(admin_required)])
async def load_m3us(m3u_files: List[Dict[str, str]], background_tasks: BackgroundTasks):


    task_id = str(uuid.uuid4())
    progress_tracker.create_task(task_id)
    
    m3u_paths = [m3u_file['filePath'] for m3u_file in m3u_files]

    try:
        # Add the task to background processing
        background_tasks.add_task(process_m3u_files, m3u_paths, task_id)
        return {"task_id": task_id, "message": "M3U processing started"}
    except Exception as e:
        progress_tracker.set_error(task_id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/load-m3u/progress/{task_id}")
async def get_load_progress(task_id: str):
    progress = progress_tracker.get_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return progress

async def process_m3u_files(m3u_paths: List[str], task_id: str):
    try:
        total_files = len(m3u_paths)

        for i, m3u_file in enumerate(m3u_paths):
            m3u_file = os.path.normpath(m3u_file)
            base_name = os.path.basename(m3u_file).split('.m3u')[0]
            output_dir = f'./results/Result_{base_name}'
            
            # Update status to show which file is being processed
            progress_tracker.update_stage_progress(task_id, 'parse', 0)
            progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Parsing)")

            # Parse M3U (incrementally update progress)
            movies, series = parse_m3u(m3u_file)
            for progress in range(0, 101, 20):
                progress_tracker.update_stage_progress(task_id, 'parse', progress)
                progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Parsing {progress}%)")
                await asyncio.sleep(0.1)

            # Write STRM files (incremental updates)
            progress_tracker.update_stage_progress(task_id, 'strm', 0)
            progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Writing STRM files)")
            max_workers = max(1, os.cpu_count() - 2)
            write_strm_files(movies, output_dir, 'movies', max_workers)
            write_strm_files(series, output_dir, 'series', max_workers)
            for progress in range(0, 101, 25):
                progress_tracker.update_stage_progress(task_id, 'strm', progress)
                progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Writing STRM {progress}%)")
                await asyncio.sleep(0.1)

            # Create JSON (incrementally update progress)
            progress_tracker.update_stage_progress(task_id, 'json', 0)
            progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Creating JSON)")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            create_json(movies, output_dir, 'movies')
            create_json(series, output_dir, 'series')
            for progress in range(0, 101, 50):
                progress_tracker.update_stage_progress(task_id, 'json', progress)
                progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Creating JSON {progress}%)")
                await asyncio.sleep(0.1)

            # Insert into the database (final stage)
            progress_tracker.update_stage_progress(task_id, 'db', 0)
            progress_tracker.update_status(task_id, f"Processing file {i + 1}/{total_files}: {base_name}.m3u (Inserting into database)")
            movies_json_path = os.path.join(output_dir, 'movies.json')
            series_json_path = os.path.join(output_dir, 'series.json')
            await insert_all_json_movies([movies_json_path])
            await insert_all_json_series([series_json_path])
            progress_tracker.update_stage_progress(task_id, 'db', 100)
            progress_tracker.update_status(task_id, f"Completed processing {base_name}.m3u")

        # Mark the task as complete
        progress_tracker.complete_task(task_id)
    except Exception as e:
        progress_tracker.set_error(task_id, f"Error processing files: {str(e)}")
        raise



@router.get("/get-providers", dependencies=[Depends(admin_required)])
async def get_providers() -> List[Provider]:  
    try:
        providers = await get_provider_data()
        return providers
    except Exception as e:
        print(f"Error getting providers: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
progress_store: Dict[str, float] = {}
progress_lock = Lock()
provider_store: Dict[str, str] = {}
def count_files_and_folders(path: str) -> int:
    """Count the total number of files and folders in the directory."""
    total_count = 0
    for root, dirs, files in os.walk(path):
        total_count += len(dirs) + len(files)
    return total_count

def run_deletion_task(providers: List[Provider], task_id: str):

    """Delete providers' files and folders recursively while tracking progress."""
    total_items = 0
    completed_items = 0

    # Calculate total items for all providers
    for provider in providers:
        total_items += count_files_and_folders(provider.path)

    for provider in providers:
        # Track the current provider being processed
        with progress_lock:
            provider_store[task_id] = provider.name

        # Recursively delete files and folders
        for root, dirs, files in os.walk(provider.path, topdown=False):
            # Delete files
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                completed_items += 1

                # Update progress
                with progress_lock:
                    progress = (completed_items / total_items) * 100
                    progress_store[task_id] = progress

            # Delete directories if empty
            for directory in dirs:
                dir_path = os.path.join(root, directory)
                if not os.listdir(dir_path):  # Check if the directory is empty
                    os.rmdir(dir_path)
                    completed_items += 1

                    # Update progress
                    with progress_lock:
                        progress = (completed_items / total_items) * 100
                        progress_store[task_id] = progress

        # Delete the root directory (provider.path) if empty
        if not os.listdir(provider.path):
            os.rmdir(provider.path)
            completed_items += 1

            # Update progress
            with progress_lock:
                progress = (completed_items / total_items) * 100
                progress_store[task_id] = progress

    # Finalize task and clear the current provider
    with progress_lock:
        progress_store[task_id] = 100.0
        provider_store[task_id] = None


@router.post("/delete-providers", dependencies=[Depends(admin_required)])
async def delete_providers(providers: List[Provider], background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    with progress_lock:
        progress_store[task_id] = 0.0  # Initialize progress

    await delete_all_providers(providers)
    # Add the task to background tasks
    background_tasks.add_task(run_deletion_task, providers, task_id)

    return {"task_id": task_id, "message": "Deletion task started."}




@router.get("/delete-progress")
async def delete_progress(task_id: str):

        
    with progress_lock:
        progress = progress_store.get(task_id, 0.0)
        current_provider = provider_store.get(task_id)
        
    response_data = {
        "progress": progress,
        "completed": progress >= 100.0,
        "provider": current_provider if progress < 100.0 else None
    }
    
    return response_data
