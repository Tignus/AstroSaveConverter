import os
import re
from cogs import AstroLogging as Logger
from utils import join_paths
from io import BytesIO


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
            The AstroSAve object

        Exception:
            None
        """
        self.name = save_name  # User-defined save name + YYYY.MM.dd-HH.mm.ss
        self.chunks_names = chunks_names  # Names of the all the chunks composing the save

    def convert_to_steam(self, source) -> BytesIO:
        """Exports a save to the disk in its Steam file format

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
