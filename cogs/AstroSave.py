from __future__ import annotations
import os
import re
from typing import List, Tuple
from io import BytesIO

from cogs import AstroLogging as Logger
from utils import is_a_file, list_folder_content, join_paths


XBOX_CHUNK_SIZE = int.from_bytes(b'\x01\x00\x00\x00', byteorder='big')


class AstroSave():
    """The Astroneer Save Class.

        This object represents an Astroneer save

        Attributes:
            save_name -- Name of the save
            chunks_names -- Names of the chunks constituting the save

        Methods:
            export_to_steam() -- Writes the save to disk
            rename() -- Renames the save
    """

    def __init__(self, save_name, chunks_names):
        """Initiates a save object

        Arguments:
            save_name -- Name of the save
            chunks_names -- Names of the chunks constituting the save

        Returns:
            The AstroSave object

        Exception:
            None
        """
        self.name = save_name  # User-defined save name + '$' + YYYY.MM.dd-HH.mm.ss
        self.chunks_names = chunks_names  # Names of the all the chunks composing the save

    @staticmethod
    # TODO how to mypy the return -> List[AstroSave]
    def init_saves_list_from(steamsave_files_list: List[str]) -> List[AstroSave]:
        """
        TODO Explains that the chunks are empty and that they will have to be initialized later
        """
        saves_list = []

        for save_file in steamsave_files_list:

            current_save_name = re.search(r'(.*)\.savegame', save_file).group(1)
            saves_list.append(AstroSave(current_save_name,
                                        None))
        return saves_list

    def convert_to_steam(self, source: str) -> BytesIO:
        """Exports a save to a buffer in its Steam file format

        The save is returned in a buffer representing a unique file
        obtained by concatenating all its chunks

        Arguments:
            source: Where to read the chunks of the save

        Returns:
            A buffer containing the Steam save
        """
        buffer = BytesIO()
        for chunk_name in self.chunks_names:
            chunk_file_path = join_paths(source, chunk_name)

            with open(chunk_file_path, 'rb') as chunk_file:
                buffer.write(chunk_file.read())
        return buffer

    def convert_to_xbox(self, source: str) -> Tuple[List[str], List[BytesIO]]:
        """Exports a save as a tuple in its Xbox file format

        The save is returned as a tuple (chunks names, chunk buffers) representing all of its chunks
        Each element of the list is a chunk of the save.
        The order of the elements matters.

        Arguments:
            source: In which folder to read the Steam save

        Returns:
            A tuple containing the names and the buffers of the Xbox chunks
        """
        # open the file file_path (AstroSave)
        #   every XBOX_CHUNK_SIZE
        #       split into a chunk -> List[buffer(chunk)]
        #       generate 1 UIID, append it to the save object chunk names (check that it doesnt exist in the appdata wgs folder)

        return ([], [])  # TODO
        # buffer = BytesIO()
        # for chunk_name in self.chunks_names:
        #     chunk_file_path = join_paths(source, chunk_name)

        #     with open(chunk_file_path, 'rb') as chunk_file:
        #         buffer.write(chunk_file.read())
        # return buffer

    def get_file_name(self):
        return self.name + '.savegame'

    def rename(self, new_name):
        """Renames a save

        We chosed to limit the characters to [a-zA-Z0-9] because we
        have no idea what are the characters supported by Astroneer
        Also the max length is 30 because somewhere above 30 won't fit
        into the chunk name once the save becomes multi-chunks when it
        grows and that might crash the game (test pending)

        Exception:
            ValueError if any character is not alphanumeric or if length > 30 or if new name is empty
        """
        if (new_name == ''):
            raise ValueError
        # We check less characters than the alphanum set because we're unsure of the
        # supported set by Astroneer
        if (new_name == '') or re.search(r'[^a-zA-Z0-9]', new_name) != None or len(new_name) > 30:
            raise ValueError

        date_string = self.name.split("$")[1]
        self.name = new_name + '$' + date_string

    @staticmethod
    def get_steamsaves_list(path) -> list:
        """List all Steam saves in a folder

        Arguments:
            path -- path where to search for Steam saves

        Returns:
            Returns a list of all Steam saves found (only filenames)

        Exception:
            None
        """
        folder_content = list_folder_content(path)
        steamsaves_list = [file for file in folder_content if AstroSave.is_a_steamsave_file(join_paths(path, file))]

        if not steamsaves_list or len(steamsaves_list) == 0:
            raise FileNotFoundError

        return steamsaves_list

    @staticmethod
    def is_a_steamsave_file(path) -> bool:
        return is_a_file(path) and path.rfind('.savegame') != -1
