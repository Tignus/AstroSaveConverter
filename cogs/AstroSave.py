from __future__ import annotations
"""Representation of an Astroneer save and related helpers."""

import os
import re
import uuid
from typing import List, Tuple
from io import BytesIO

from cogs import AstroLogging as Logger
from utils import is_a_file, list_folder_content, join_paths


XBOX_CHUNK_SIZE = int.from_bytes(b'\x01\x00\x00\x00', byteorder='big')


class AstroSave:
    """In-memory representation of an Astroneer save."""

    def __init__(self, save_name: str, chunks_names: List[str]) -> None:
        """Create a new ``AstroSave`` instance.

        Args:
            save_name: Name of the save.
            chunks_names: Names of the chunks constituting the save.
        """
        self.name = save_name  # User-defined save name + '$' + YYYY.MM.dd-HH.mm.ss
        self.chunks_names = chunks_names  # Names of the all the chunks composing the save

    @staticmethod
    def init_saves_list_from(steamsave_files_list: List[str]) -> List['AstroSave']:
        """Create ``AstroSave`` objects for a list of Steam save files."""
        saves_list: List[AstroSave] = []
        for save_file in steamsave_files_list:
            current_save_name = re.search(r'(.*)\.savegame', save_file).group(1)
            saves_list.append(AstroSave(current_save_name, []))
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

    def convert_to_xbox(self, source: str) -> Tuple[List[uuid.UUID], List[BytesIO]]:
        """Split a Steam save file into Xbox-formatted chunks.

        Args:
            source: Path to the Steam ``.savegame`` file.

        Returns:
            Tuple[List[uuid.UUID], List[BytesIO]]: Generated UUIDs and chunk buffers.
        """
        buffer_uuids: List[uuid.UUID] = []
        buffers: List[BytesIO] = []
        self.chunks_names = []

        len_read = XBOX_CHUNK_SIZE
        save_file_path = source

        with open(save_file_path, 'rb') as save_file:
            while len_read == XBOX_CHUNK_SIZE:
                buffer = BytesIO()
                file_uuid = uuid.uuid4()
                Logger.logPrint(f'UUID generated: {file_uuid}', "debug")

                buffer.write(save_file.read(XBOX_CHUNK_SIZE))

                len_read = len(buffer.getvalue())

                self.chunks_names.append(file_uuid.hex.upper())
                buffer_uuids.append(file_uuid)
                buffers.append(buffer)

        return (buffer_uuids, buffers)

    def regenerate_uuid(self, chunk_index: int) -> uuid.UUID:
        """Generate a new UUID for the chunk at ``chunk_index``."""
        new_uuid = uuid.uuid4()
        self.chunks_names[chunk_index](new_uuid.hex.upper())
        return new_uuid

    def get_file_name(self) -> str:
        """Return the filename corresponding to this save."""
        return self.name + '.savegame'

    def rename(self, new_name: str) -> None:
        """Rename the save, enforcing character and length limits.

        We chosed to limit the characters to [a-zA-Z0-9] because we
        have no idea what are the characters supported by Astroneer
        Also the max length is 30 because somewhere above 30 won't fit
        into the chunk name once the save becomes multi-chunks when it
        grows and that might crash the game (test pending)

        Args:
            new_name: New base name for the save.

        Raises:
            ValueError: If ``new_name`` is empty, non-alphanumeric or too long.
        """
        if new_name == '' or re.search(r'[^a-zA-Z0-9]', new_name) or len(new_name) > 30:
            raise ValueError

        date_string = self.name.split("$")[1]
        self.name = new_name + '$' + date_string

    @staticmethod
    def get_steamsaves_list(path: str) -> List[str]:
        """List all Steam saves in a folder."""
        folder_content = list_folder_content(path)
        steamsaves_list = [
            file for file in folder_content
            if AstroSave.is_a_steamsave_file(join_paths(path, file))
        ]

        if not steamsaves_list:
            raise FileNotFoundError

        return steamsaves_list

    @staticmethod
    def is_a_steamsave_file(path: str) -> bool:
        """Return ``True`` if ``path`` refers to a Steam save file."""
        return is_a_file(path) and path.rfind('.savegame') != -1
