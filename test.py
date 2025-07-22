import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
try:
    import pyheif
except ImportError:
    pyheif = None
from io import BytesIO
import sys

# Extracts the original date from EXIF metadata of JPEG images
def get_exif_date(filepath):
    try:
        image = Image.open(filepath)  # Open image file
        exif_data = image._getexif()  # Get EXIF metadata
        if exif_data:
            for tag_id, value in exif_data.items():  # Iterate over metadata tags
                tag = TAGS.get(tag_id, tag_id)  # Get tag name
                if tag == 'DateTimeOriginal':  # Look for original date tag
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')  # Parse date
    except Exception:
        pass  # Ignore errors and return None
    return None

# Extracts the original date from HEIC images using pyheif and PIL
def get_heic_date(filepath):
    if pyheif is None:
        return None  # pyheif not available
    try:
        heif_file = pyheif.read(filepath)  # Read HEIC file
        for meta in heif_file.metadata or []:  # Iterate over metadata blocks
            if meta['type'] == 'Exif':  # Look for EXIF metadata
                img = Image.open(BytesIO(meta['data']))  # Open EXIF data as image
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal':
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    return None

# Gets the file modification time for video files
def get_video_date(filepath):
    try:
        ts = os.path.getmtime(filepath)  # Get last modification time
        return datetime.fromtimestamp(ts)  # Convert to datetime object
    except Exception:
        return None

# Determines the date for a file based on its extension and available metadata
def get_file_date(filepath):
    ext = filepath.lower().split('.')[-1]  # Get file extension
    if ext in ['jpg', 'jpeg']:
        date = get_exif_date(filepath)  # Try to get EXIF date
        if date:
            return date
    elif ext == 'heic':
        date = get_heic_date(filepath)  # Try to get HEIC date
        if date:
            return date
    elif ext in ['mov', 'mp4', 'avi', 'mkv']:
        date = get_video_date(filepath)  # Use modification time for videos
        if date:
            return date
    # If no metadata, fallback to file modification time
    try:
        ts = os.path.getmtime(filepath)
        return datetime.fromtimestamp(ts)
    except Exception:
        return None

# Main function to sort and copy pictures/videos into folders by year and month
def sort_pictures(src_dir, dest_dir):
    supported_exts = ['.jpg', '.jpeg', '.heic', '.mov', '.mp4', '.avi', '.mkv']  # Supported file types
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    # Walk through all files in the source directory
    for root, _, files in os.walk(src_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()  # Get file extension
            if ext in supported_exts:
                src_path = Path(root) / file  # Full source file path
                date = get_file_date(str(src_path))  # Get date for sorting
                if date:
                    year = str(date.year)  # Extract year
                    month = f"{date.month:02d}"  # Extract month (zero-padded)
                else:
                    year = "unknown"
                    month = "unknown"
                # Create target directory based on year and month
                target_dir = dest_dir / year / month
                target_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                target_path = target_dir / file  # Destination file path
                # Avoid overwriting files by renaming if necessary
                if target_path.exists():
                    base, ext = os.path.splitext(file)
                    i = 1
                    while True:
                        new_name = f"{base}_{i}{ext}"  # Append counter to filename
                        target_path = target_dir / new_name
                        if not target_path.exists():
                            break
                        i += 1
                # Copy the file to the target directory
                shutil.copy2(src_path, target_path)  # Copy file with metadata
                print(f"Copied {src_path} -> {target_path}")

# Entry point: checks arguments and calls sort_pictures
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test.py <source_dir> <destination_dir>")
    else:
        sort_pictures(sys.argv[1], sys.argv[2])
