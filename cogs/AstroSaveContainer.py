import os
import hexdump
import re

from utils import is_a_file, list_folder_content, join_paths

from cogs.AstroSave import AstroSave
from cogs import AstroLogging as Logger

CHUNK_METADATA_SIZE = 160  # Length of a chunk metadata found in a save container


class AstroSaveContainer():
    """
        The Astroneer Save Container Class.

        This object represents an Astroneer save container

        Attributes:
            path -- Path of the container file
            header -- Header of the container file
            chunk_count -- Number of save chunks in the container file
            save_list -- List of all the saves contained in the file

        Methods:
            print_container() -- Prints the saves
            xbox_to_steam(save_to_convert) -- Convert one or several saves
            is_valid_container_header(header) -- Validate the header
            extract_name_from_chunk(chunk) -- Extract a save name from a chunk
            extract_chunk_file_name_from_chunk(chunk) -- Extract the file name of a chunk
            chunk_grab_bytes_to_string(chunk, index, n) -- Read some bytes of a chunk
            reverse_string(string) -- Convert a string to its reversed form
            convert_chunk_name_to_file_name(string) -- Convert the name of a chunk to its corresponding file name
            string_to_hex(string) -- Convert a string to its hexadecimal form
    """

    def __init__(self, container_file_path):
        """
        Extracts the saves from an Astroneer save container

        Reads the container file, divides it into chunks and
        regroups the chunks into save objects

        Arguments:
            container_file_path -- Path to the container file

        Returns:
            The AstroSaveContainer object 

        Exception:
            None
        """
        self.full_path = container_file_path
        self.save_list = []
        Logger.logPrint(f'full_path: {self.full_path}', "debug")

        with open(self.full_path, "rb") as container:
            # The Astroneer file type is contained in at least the first 2 bytes of the file
            self.header = container.read(2)

            if not self.is_valid_container_header(self.header):
                raise Exception(
                    f'The save container {self.full_path} is not valid (First two bytes:{self.header})')
            # Skipping 2 bytes that may be part of the header
            container.read(2)

            # Next 4 bytes are the number of saves chunk
            self.chunk_count = int.from_bytes(
                container.read(4), byteorder='little')

            # Parsing saves chunks
            current_save_name = None
            for _ in range(self.chunk_count):
                current_chunk = container.read(CHUNK_METADATA_SIZE)
                current_chunk_name = self.extract_name_from_chunk(
                    current_chunk)
                Logger.logPrint(f'Save: {current_chunk_name}', "debug")

                if current_chunk_name != current_save_name:
                    if current_save_name != None:
                        # Parsing a new save, storing the current save
                        self.save_list.append(AstroSave(current_save_name,
                                                        current_chunks_names))

                    current_chunks_names = []
                    current_save_name = current_chunk_name

                chunk_file_name = self.extract_chunk_file_name_from_chunk(current_chunk)
                Logger.logPrint(f'Processed chunk: {chunk_file_name}', "debug")

                current_chunks_names.append(chunk_file_name)

            # Saving the last save of the container file
            self.save_list.append(AstroSave(current_save_name,
                                            current_chunks_names))

    def is_valid_container_header(self, header):
        """
        Validates the container header against the expected save container header

        Arguments:
            header -- The header to validate

        Returns:
            True if the header is correct
            False otherwise 

        Exception:
            None
        """
        # A save container starts with those 2 bytes
        expected_header = b'\x04\x00'
        return header == expected_header

    def extract_name_from_chunk(self, chunk):
        """
        Extracts the save name inside a chunk

        Arguments:
            chunk -- Chunk from which to extract the save name

        Returns:
            The name of the save 

        Exception:
            None
        """
        # Reading the whole UTF-16 string in the chunk
        utf_16_encoded_text = chunk[0:CHUNK_METADATA_SIZE -
                                    32].decode('utf-16le', errors='ignore')

        # The seperator is either '$$' in case of multi-chunk save
        # or '\x00' if only one chunk
        return re.split('[$]{2}|[\\x00]', utf_16_encoded_text)[0]

    def extract_chunk_file_name_from_chunk(self, chunk):
        """
        Extracts the file name of a chunk 

        Arguments:
            chunk -- Chunk from which to extract the file name

        Returns:
            The name of the file 

        Exception:
            None
        """
        chunk_file_name = ''
        partial_name = ''
        i = CHUNK_METADATA_SIZE - 16

        (partial_name, i) = self.chunk_grab_bytes_to_string(chunk, i, 4)
        chunk_file_name = self.convert_chunk_name_to_file_name(partial_name)

        (partial_name, i) = self.chunk_grab_bytes_to_string(chunk, i, 2)
        chunk_file_name += self.convert_chunk_name_to_file_name(partial_name)

        (partial_name, i) = self.chunk_grab_bytes_to_string(chunk, i, 2)
        chunk_file_name += self.convert_chunk_name_to_file_name(partial_name)

        (partial_name, i) = self.chunk_grab_bytes_to_string(chunk, i, 8)
        chunk_file_name += self.string_to_hex(partial_name)

        return chunk_file_name

    def chunk_grab_bytes_to_string(self, chunk, index, n):
        """
        Reads bytes from a chunk and put them in a string

        Arguments:
            chunk -- Chunk from which to read bytes
            index -- Index from where to start reading
            n -- Number of bytes to read

        Returns:
            The extracted string 

        Exception:
            None
        """
        extracted_string = ''
        for _ in range(n):
            extracted_string += chr(chunk[index])
            index += 1

        return (extracted_string, index)

    def reverse_string(self, string):
        """
        Reverses a string

        Arguments:
            string -- string to reverse

        Returns:
            The reversed string 

        Exception:
            None
        """
        return string[:: -1]

    def convert_chunk_name_to_file_name(self, string):
        """
        Converts the chunk name to its file name

        Arguments:
            string -- string to convert

        Returns:
            The converted string 

        Exception:
            None
        """
        return self.string_to_hex(self.reverse_string(string))

    def string_to_hex(self, string):
        """
        Converts a string to its hexadecimal characters in upper case latin1 encoding

        Arguments:
            string -- string to convert

        Returns:
            The converted string 

        Exception:
            None
        """
        return string.encode('latin1').hex().upper()

    @staticmethod
    def get_containers_list(path) -> list:
        """List all containers in a folder

        Arguments:
            path -- path where to search containers

        Returns:
            Returns a list of all containers found (only filename of container)

        Exception:
            None
        """
        folder_content = list_folder_content(path)
        containers_list = [
            file for file in folder_content if AstroSaveContainer.is_a_container_file(join_paths(path, file))]

        if not containers_list or len(containers_list) == 0:
            raise FileNotFoundError

        return containers_list

    @staticmethod
    def is_a_container_file(path) -> bool:
        return is_a_file(path) and path.rfind('container') != -1
