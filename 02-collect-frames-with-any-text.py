from PIL import Image
from os import listdir, makedirs, remove
from os.path import join, basename, splitext
from pytesseract import image_to_string
from typing import List
from sys import platform
import ffmpeg

if platform == 'win32':
    from pytesseract import pytesseract
    pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

FFMPEG_EXECUTABLE = "./bin/ffmpeg.exe" if platform == "win32" else "ffmpeg"

EPISODE_DIRECTORY = "./episodes/"
FRAME_DIRECTORY = "./frames/"


class Episode:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.frame_directory = self.__create_frame_directory(filename)
    
    def __create_frame_directory(self, filename: str) -> str:
        directory_name = splitext(basename(filename))[0]
        directory_path = join(FRAME_DIRECTORY, directory_name)
        
        makedirs(directory_path, exist_ok=True)
        return directory_path
    
    def extract_frames(self) -> None:
        frame_output_path = join(self.frame_directory, "./%04d.jpg")
        ffmpeg.input(self.filename, ) \
            .output(frame_output_path, vf="fps=1/2") \
                .overwrite_output() \
                    .run(cmd=FFMPEG_EXECUTABLE)


def get_episodes() -> List[Episode]:
    return [Episode(join(EPISODE_DIRECTORY, filename)) for filename in listdir(EPISODE_DIRECTORY) if not filename.startswith(".")]


def is_directory_empty(directory: str) -> bool:
    return len(listdir(directory)) == 0


def clean_images_from_non_ocrable_ones(directory: str) -> None:
    for filename in listdir(directory):
        image = Image.open(join(directory, filename))
        text = image_to_string(image)

        if text == "":
            absolute_path = join(directory, filename)
            print(f"Image {absolute_path} is not OCRable, removing")
            remove(absolute_path)


def extract_frames_from_episodes(episodes: List[Episode]) -> None:
    for episode in episodes:
        if not is_directory_empty(episode.frame_directory):
            continue

        print(f"Extracting frames from {episode.filename}")
        episode.extract_frames()

        clean_images_from_non_ocrable_ones(episode.frame_directory)


def main():
    episodes = get_episodes()
    extract_frames_from_episodes(episodes)


if __name__ == "__main__":
    main()
