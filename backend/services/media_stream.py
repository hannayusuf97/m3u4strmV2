import subprocess
import re

def parse_duration(duration_str):
    """Parses the duration string from ffmpeg and rounds it to the nearest second."""
    # Split the duration string into hours, minutes, and seconds
    parts = duration_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(float, parts)
        total_seconds = int(round(hours * 3600 + minutes * 60 + seconds))
        # Convert back to HH:MM:SS format
        rounded_duration = f"{total_seconds // 3600}:{(total_seconds % 3600) // 60:02}:{total_seconds % 60:02}"
        return rounded_duration
    return "Unknown"


def get_video_info(file_path):
    """Get information about the video file using ffmpeg."""
    try:
        # Run ffmpeg command to get video file info
        result = subprocess.run(
            ['ffmpeg', '-i', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        info = result.stderr  # ffmpeg outputs info to stderr

        # Initialize duration and resolution
        duration = "Error"
        resolution = "Error"

        # Regex patterns for duration and resolution
        duration_pattern = re.compile(r'Duration:\s+(\d+:\d+:\d+\.\d+)')
        resolution_pattern = re.compile(r'(\d{2,4})\s*x\s*(\d{2,4})')

        # Search for duration
        duration_match = duration_pattern.search(info)
        if duration_match:
            duration_str = duration_match.group(1) 
            duration = parse_duration(duration_str)

        # Search for resolution
        resolution_match = resolution_pattern.search(info)
        if resolution_match:
            resolution = f"{resolution_match.group(1)}x{resolution_match.group(2)}"

        return duration, resolution
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        return "Error", "Error"
