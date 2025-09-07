"""Parsing and handling of Astroneer save container files."""

import os
import hexdump
import re

from utils import is_a_file, list_folder_content, join_paths

from cogs.AstroSave import AstroSave
from cogs import AstroLogging as Logger

CHUNK_METADATA_SIZE = 160  # Length of a chunk metadata found in a save container


class AstroSaveContainer:
    """Represent an Astroneer save container and its contents."""

    def __init__(self, container_file_path: str) -> None:
        """Load saves from a container file.

        Args:
            container_file_path: Path to the container file.
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

    def is_valid_container_header(self, header: bytes) -> bool:
        """Validate a container file header."""
        expected_header = b'\x04\x00'
        return header == expected_header

    def extract_name_from_chunk(self, chunk: bytes) -> str:
        """Extract the save name stored in a chunk.

        Args:
            chunk: Raw chunk bytes.

        Returns:
            str: Name of the save.
        """
        # Reading the whole UTF-16 string in the chunk
        utf_16_encoded_text = chunk[0:CHUNK_METADATA_SIZE -
                                    32].decode('utf-16le', errors='ignore')

        # The seperator is either '$$' in case of multi-chunk save
        # or '\x00' if only one chunk
        return re.split('[$]{2}|[\\x00]', utf_16_encoded_text)[0]

    def extract_chunk_file_name_from_chunk(self, chunk: bytes) -> str:
        """Extract the filename associated with a chunk.

        Args:
            chunk: Chunk to inspect.

        Returns:
            str: Filename derived from the chunk metadata.
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

    def chunk_grab_bytes_to_string(self, chunk: bytes, index: int, n: int):
        """Read ``n`` bytes from ``chunk`` starting at ``index``.

        Args:
            chunk: Source bytes.
            index: Starting index.
            n: Number of bytes to read.

        Returns:
            tuple[str, int]: Extracted string and new index position.
        """
        extracted_string = ''
        for _ in range(n):
            extracted_string += chr(chunk[index])
            index += 1

        return (extracted_string, index)

    def reverse_string(self, string: str) -> str:
        """Return ``string`` reversed."""
        return string[::-1]

    def convert_chunk_name_to_file_name(self, string: str) -> str:
        """Convert a chunk's display name to its filename."""
        return self.string_to_hex(self.reverse_string(string))

    def string_to_hex(self, string: str) -> str:
        """Convert ``string`` to uppercase hexadecimal using Latin-1 encoding."""
        return string.encode('latin1').hex().upper()

    @staticmethod

    def get_containers_list(path: str) -> list:
        """Return container filenames found in a directory.

        Args:
            path: Directory to search for ``container.*`` files.

        Returns:
            List of container filenames located in ``path``.

        Raises:
            FileNotFoundError: If no ``container.*`` files are found.
        """
        folder_content = list_folder_content(path)
        containers_list = [
            file for file in folder_content if AstroSaveContainer.is_a_container_file(join_paths(path, file))]

        if not containers_list or len(containers_list) == 0:
            raise FileNotFoundError

        return containers_list

    @staticmethod
    def create_empty_container(path: str) -> None:
        """Create an empty container file in ``path``.

        Args:
            path: Directory where the blank container should be created.
        """
        container_full_path = join_paths(path, 'container.1')
        with open(container_full_path, 'wb') as container:
            container.write(b'\x04\x00\x00\x00\x00\x00\x00\x00')

    @staticmethod
    def is_a_container_file(path) -> bool:
        """Return ``True`` if ``path`` looks like a save container.

        Args:
            path: File path to inspect.

        Returns:
            bool: ``True`` if the file name contains ``'container'``.
        """
        return is_a_file(path) and path.rfind('container') != -1
