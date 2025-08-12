import shutil
import sys
import os

from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
try:
    import pyheif
except ImportError:
    pyheif = None
from io import BytesIO

class Sorter:

    def __init__(self, src_dir, dest_dir, copy=True, months=False, logfile=False):
        self.mlist = ["01_Januar", "02_Februar", "03_Maerz", "04_April", "05_Mai", "06_Juni", "07_Juli", 
                      "08_August", "09_September", "10_Oktober", "11_November", "12_Dezember"]
        self.src_dir = Path(src_dir)
        self.dest_dir = Path(dest_dir)
        self.copy = copy
        self.rename_months = months
        self.logfile = logfile
        self.supported_exts = ['.jpg', '.jpeg', '.png', '.heic', '.mov', '.mp4', '.avi', '.mkv']
        
    def sort_media(self):
        for root, _, files in os.walk(self.src_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_exts:
                    src_path = Path(root) / file
                    date = self.get_file_date(str(src_path))
                    if date:
                        year = str(date.year)
                        if self.rename_months:
                            month = self.mlist[date.month - 1]
                        else:
                            month = f"{date.month:02d}"
                        day = f"{date.day:02d}"
                    else:
                        year = "unknown"
                        month = "unknown"
                        day = "unknown"
                    target_dir = self.dest_dir / year / month / day
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_path = target_dir / file
                    if target_path.exists():
                        base, ext = os.path.splitext(file)
                        i = 1
                        while True:
                            new_name = f"{base}_{i}{ext}"
                            target_path = target_dir / new_name
                            if not target_path.exists():
                                break
                            i += 1
                    if self.copy:
                        shutil.copy2(src_path, target_path)
                        if self.logfile:
                            self.__append_log(f"Copied {src_path} -> {target_path}")
                    else:
                        shutil.move(src_path, target_path)
                        if self.logfile:
                            self.__append_log(f"Moved {src_path} -> {target_path}")
                else:
                    src_path = Path(root) / file
                    self.__append_notsupported(f"Skipped unsupported file: {src_path}")
    # def sort_media(self):
    #     for root, _, files in os.walk(self.src_dir):
    #         for file in files:
    #             ext = os.path.splitext(file)[1].lower()
    #             if ext in self.supported_exts:
    #                 src_path = Path(root) / file
    #                 date = self.get_file_date(str(src_path))
    #                 if date:
    #                     year = str(date.year)
    #                     if self.rename_months:
    #                         month = self.mlist[date.month - 1]
    #                     else:
    #                         month = f"{date.month:02d}"
    #                 else:
    #                     year = "unknown"
    #                     month = "unknown"
    #                 target_dir = self.dest_dir / year / month
    #                 target_dir.mkdir(parents=True, exist_ok=True)
    #                 target_path = target_dir / file
    #                 if target_path.exists():
    #                     base, ext = os.path.splitext(file)
    #                     i = 1
    #                     while True:
    #                         new_name = f"{base}_{i}{ext}"
    #                         target_path = target_dir / new_name
    #                         if not target_path.exists():
    #                             break
    #                         i += 1
    #                 if self.copy:
    #                     shutil.copy2(src_path, target_path)
    #                     if self.logfile:
    #                         self.__append_log(f"Copied {src_path} -> {target_path}")
    #                 else:
    #                     shutil.move(src_path, target_path)
    #                     if self.logfile:
    #                         self.__append_log(f"Moved {src_path} -> {target_path}")
                    

    # Determines the date for a file based on its extension and available metadata
    def get_file_date(self, filepath):
        ext = filepath.lower().split('.')[-1]  # Get file extension
        if ext in ['jpg', 'jpeg', 'png']:
            date = self.__get_exif_date(filepath)  # Try to get EXIF date
            if date:
                return date
        elif ext == 'heic':
            date = self.__get_heic_date(filepath)  # Try to get HEIC date
            if date:
                return date
        elif ext in ['mov', 'mp4', 'avi', 'mkv']:
            date = self.__get_video_date(filepath)  # Use modification time for videos
            if date:
                return date
        # If no metadata, fallback to file modification time
        try:
            ts = os.path.getmtime(filepath)
            return datetime.fromtimestamp(ts)
        except Exception:
            return None
        
    # Extracts the original date from EXIF metadata of JPEG images
    def __get_exif_date(self, filepath):
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
    def __get_heic_date(self, filepath):
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
    def __get_video_date(self, filepath):
        try:
            ts = os.path.getmtime(filepath)  # Get last modification time
            return datetime.fromtimestamp(ts)  # Convert to datetime object
        except Exception:
            return None
        
    def __append_log(self, line):
        try:
            with open('log.txt', 'a') as f:
                f.write(line + '\n')
        except Exception as e:
            if self.verbose:
                print(f"Error appending to log.txt: {e}")

    def __append_notsupported(self, line):
        try:
            with open('error.txt', 'a') as f:
                f.write(line + '\n')
        except Exception as e:
            if self.verbose:
                print(f"Error appending to log.txt: {e}")