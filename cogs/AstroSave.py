import os
import re
from cogs.AstroLogging import AstroLogging


XBOX_CHUNK_SIZE = int.from_bytes(b'\x01\x00\x00\x00', byteorder='big')


class AstroSave():
    """
        The Astroneer Save Class.

        This object represents an Astroneer save

        Attributes:
            save_name -- Name of the save
            chunks_names -- Names of the chunks constituting the save

        Methods:
            export_to_steam() -- Writes the save to disk
            rename() -- Renames the save
    """

    def __init__(self, save_name, chunks_names):
        """
        Initiates a save object

        Arguments:
            save_name -- Name of the save
            chunks_names -- Names of the chunks constituting the save

        Returns:
            The AstroSAve object 

        Exception:
            None
        """
        self.save_name = save_name  # User-defined save name + YYYY.MM.dd-HH.mm.ss
        self.chunks_names = chunks_names  # Names of the all the chunks composing the save

    def export_to_steam(self, path):
        """
        Exports a save to the disk in its Steam file format

        The save is written to the disk in a unique file
        obtained by concatenating all its chunks

        Arguments:
            None

        Returns:
            None 

        Exception:
            None
        """
        file_name = self.save_name+'.savegame'

        while os.path.exists(os.path.join(path, file_name)):
            is_overwrite = None
            while is_overwrite != 'y' and is_overwrite != 'n':
                AstroLogging.logPrint(
                    f'\nFile {file_name} already exists, overwrite it ? (y/n)')
                is_overwrite = input().lower()

            if is_overwrite == 'n':
                self.rename()
                file_name = self.save_name+'.savegame'
            elif is_overwrite == 'y':
                break

        with open(os.path.join(path, file_name), "wb") as steam_save:
            for chunk_name in self.chunks_names:
                with open(os.path.join(path, chunk_name), 'rb') as chunk_file:
                    steam_save.write(chunk_file.read())

        AstroLogging.logPrint(
            f"\nSave {self.save_name} has been exported succesfully.")

    def rename(self):
        """
        Renames a save

        We chosed to limit the characters to [a-zA-Z0-9] because we
        have no idea what are the characters supported by Astroneer
        Also the max length is 30 because somewhere above 30 won't fit
        into the chunk name once the save becomes multi-chunks when it 
        grows and that might crash the game (test pending)

        Arguments:
            None

        Returns:
            None 

        Exception:
            None
        """
        old_name = self.save_name
        new_name = None
        while new_name == None:
            try:
                new_name = input(
                    f'\nNew name for {old_name.split("$")[0]}: [ENTER = unchanged] > ').upper()
                # We check less characters than the alphanum set because we're unsure of the
                # supported set by Astroneer
                if (new_name != ''):
                    if re.search(r'[^a-zA-Z0-9]', new_name) != None or len(new_name) > 30:
                        raise ValueError
                    self.save_name = new_name + \
                        '$' + old_name.split("$")[1]
            except ValueError:
                new_name = None
                AstroLogging.logPrint(
                    f'Please use only alphanum and a length < 30')
