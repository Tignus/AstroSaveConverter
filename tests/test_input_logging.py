import builtins
from unittest.mock import patch, call
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import AstroSaveScenario as scenario
from cogs.AstroConvType import AstroConvType
from cogs import AstroMicrosoftSaveFolder
from cogs.AstroSave import AstroSave


def _call_args_contains(mock, expected_call):
    return any(c == expected_call for c in mock.call_args_list)


def test_ask_conversion_type_logs_choice():
    with patch.object(builtins, 'input', side_effect=['3', '1']), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        result = scenario.ask_conversion_type()
        assert result == AstroConvType.WIN2STEAM
        assert _call_args_contains(log_mock, call('User choice: 1', 'debug'))


def test_ask_copy_target_logs_choices():
    with patch.object(builtins, 'input', side_effect=['2', '/tmp']), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        scenario.ask_copy_target('folder', 'Steam')
        assert _call_args_contains(log_mock, call('User choice: 2', 'debug'))
        assert _call_args_contains(log_mock, call('User choice: /tmp', 'debug'))


def test_ask_for_multiple_choices_logs():
    with patch.object(builtins, 'input', side_effect=['1,2']), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        result = scenario.ask_for_multiple_choices(4)
        assert result == [0, 1]
        assert _call_args_contains(log_mock, call('User choice: 1,2', 'debug'))


def test_ask_rename_saves_logs():
    save = AstroSave('OLD$2024.01.01-00.00.00', [])
    with patch.object(builtins, 'input', side_effect=['n']), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        scenario.ask_rename_saves([0], [save])
        assert _call_args_contains(log_mock, call('User choice: n', 'debug'))


def test_rename_save_logs():
    save = AstroSave('OLD$2024.01.01-00.00.00', [])
    with patch.object(builtins, 'input', side_effect=['newname']), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        scenario.rename_save(save)
        assert save.name.startswith('NEWNAME$')
        assert _call_args_contains(log_mock, call('User choice: NEWNAME', 'debug'))


def test_seek_microsoft_save_folder_logs_choice():
    with patch.object(builtins, 'input', side_effect=['3', '1']), \
         patch('cogs.AstroLogging.logPrint') as log_mock, \
         patch('cogs.AstroMicrosoftSaveFolder.get_save_folders_from_path', return_value=['a', 'b']):
        result = AstroMicrosoftSaveFolder.seek_microsoft_save_folder('x')
        assert result == 'a'
        assert _call_args_contains(log_mock, call('User choice: 3', 'debug'))
        assert _call_args_contains(log_mock, call('User choice: 1', 'debug'))

def test_ask_microsoft_target_folder_logs_choice():
    with patch.object(builtins, 'input', side_effect=['3', '1']), \
         patch.dict('os.environ', {'LOCALAPPDATA': '/tmp'}), \
         patch('glob.iglob', return_value=['dummy']), \
         patch('cogs.AstroMicrosoftSaveFolder.get_save_folders_from_path', return_value=['a', 'b']), \
         patch('cogs.AstroMicrosoftSaveFolder.get_save_details', return_value=[]), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        result = scenario.ask_microsoft_target_folder()
        assert result == 'a'
        assert _call_args_contains(log_mock, call('User choice: 3', 'debug'))
        assert _call_args_contains(log_mock, call('User choice: 1', 'debug'))


def test_backup_win_before_steam_export_logs_choice():
    with patch.object(builtins, 'input', side_effect=['4', '3']), \
         patch('cogs.AstroMicrosoftSaveFolder.find_microsoft_save_folders', side_effect=FileNotFoundError()), \
         patch('AstroSaveScenario.ask_copy_target', return_value='/tmp'), \
         patch('cogs.AstroLogging.logPrint') as log_mock:
        result = scenario.backup_win_before_steam_export()
        assert result == ''
        assert _call_args_contains(log_mock, call('User choice: 4', 'debug'))
        assert _call_args_contains(log_mock, call('User choice: 3', 'debug'))
