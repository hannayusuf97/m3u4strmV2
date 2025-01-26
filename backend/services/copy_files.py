import os
import shutil  # Import shutil for file operations
import platform  # Import platform to check the OS type


def normalize_path(path):
    """Normalize paths based on the OS. Ensure forward slashes for Ubuntu."""
    # If on Unix-like system, replace backslashes with forward slashes
    path = path.replace('\\', '/')
    return os.path.normpath(path)


def copy_movie(path):
    """Copy a folder (movie) from src to dest."""
    dest = r'./jellyfin/movies'
    
    # Normalize paths and ensure correct format
    path = normalize_path(path)
    dest = normalize_path(dest)

    if not os.path.exists(path):  # Check if the folder exists
        print(f"Folder does not exist: {path}")
        return  # Exit the function if the folder does not exist

    folder_name = os.path.basename(path)  # Get the last part of the path
    final_dest = os.path.join(dest, folder_name)   # Create the final destination path
    try:
        shutil.copytree(path, final_dest)  # Copy the folder
        print(f"Folder copied from {path} to {final_dest}")
    except Exception as e:
        print(f"Error copying folder: {e}")

def copy_and_overwrite(src, dst):
    """
    Copy files from src to dst, overwriting files in dst if they already exist.
    """
    # Ensure the destination directory exists
    os.makedirs(dst, exist_ok=True)

    # Walk through the source directory
    for root, dirs, files in os.walk(src):
        # Create corresponding directories in the destination
        relative_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, relative_path)
        os.makedirs(dest_dir, exist_ok=True)

        # Copy files, overwriting if they already exist
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)
            shutil.copy2(src_file, dest_file)
            print(f"Copied {src_file} to {dest_file}")

def copy_series(path):
    """Copy a folder from src to dest."""
    dest = r'./jellyfin/tvshows'
    dest = os.path.normpath(dest)
    if not os.path.exists(path):  # Check if the folder exists
        print(f"Folder does not exist: {path}")
        return  # Exit the function if the folder does not exist

    # Extract the last part of the path after '\\series\\'
    folder_name = os.path.basename(path)  # Get the last part of the path
    final_dest = os.path.join(dest, folder_name)  # Create the final destination path

    try:
        copy_and_overwrite(path, final_dest)  # Copy the folder
        print(f"Folder copied from {path} to {final_dest}")
    except Exception as e:
        print(f"Error copying folder: {e}")
             
def copy_episode(path):
    """Copy a single episode file from src to dest."""
    dest = r'./jellyfin/tvshows'
    dest = os.path.normpath(dest)
    if not os.path.isfile(os.path.normpath(path)):  # Check if the file exists
        print(f"File does not exist: {path}")
        return f"File does not exist: {path}"  # Exit the function if the file does not exist

    # Extract the file name
    parts = os.path.normpath(path).replace('\\', '/').split('/')
    season_nr = parts[-2]
    series_name = parts[-3]
    final_dest = os.path.join(dest, series_name,season_nr)  # Create the final destination path

    try:
        if os.path.exists(os.path.normpath(final_dest)):
            shutil.copyfile(os.path.normpath(path), os.path.normpath(final_dest))  # Copy the file
            print(f"File copied from {path} to {final_dest}")
        else:
            os.makedirs(os.path.normpath(final_dest))
            shutil.copy(os.path.normpath(path), os.path.normpath(final_dest))
    except Exception as e:
        print(f"Error copying file: {e}")


def copy_season(path):
    """Copy a season folder from src to dest."""
    dest = r'./jellyfin/tvshows'
    dest = os.path.normpath(dest)
    if not os.path.exists(os.path.normpath(path)):  # Check if the folder exists
        return f"Folder does not exist: {path}"# Exit the function if the folder does not exist

    # Extract the last part of the path
    parts = os.path.normpath(path).replace('\\', '/').split('/')
    folder_name = parts[-2]
    season_nr = parts[-1]

    final_dest = os.path.join(dest,folder_name, season_nr)  # Create the final destination path

    if os.path.exists(os.path.normpath(final_dest)):
        print(f"Destination folder already exists: {final_dest}. Removing it...")
        shutil.rmtree(os.path.normpath(final_dest))

    try:
        shutil.copytree(os.path.normpath(path), os.path.normpath(final_dest))  # Copy the folder
        print(f"Season copied from {os.path.normpath(path)} to {final_dest}")
    except Exception as e:
        print(f"Error copying season: {e}")