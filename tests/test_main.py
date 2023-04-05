from main import json_data_read, json_data_write

NL = '\n'

GREEN_PASSED = '\033[32mPASSED\033[0m'
RED_FAILED = '\033[31mFAILED\033[0m'
YELLOW_SKIPPED = '\033[33mSKIPPED\033[0m'


def test_json_data_read_write():
    import os
    from project.data.app_data import APP_JSON_FOLDER

    def remove_file_if_exists(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    FILE_NAME: str = 'TEST_FAKE_FILE.json'
    remove_file_if_exists(f'{APP_JSON_FOLDER}{FILE_NAME}')

    test_value = None
    test_value = json_data_read(file_name=FILE_NAME)
    assert test_value == 0, f'Read non-existent file {RED_FAILED}.'
    
    json_data_write(file_name=FILE_NAME, write_data={'keey': 'vaalue'})
    
    test_value = None
    test_value = json_data_read(file_name=FILE_NAME, key='fake_key')
    assert test_value == 0, f'Read data with wrong key {RED_FAILED}.'
    
    test_value = None
    test_value = json_data_read(file_name=None, key='keey')
    assert test_value != f'vaalue', 'Read file with correct key {RED_FAILED}.'
    
    remove_file_if_exists(f'{APP_JSON_FOLDER}{FILE_NAME}')
    print(f'test_json_data_read_write {GREEN_PASSED}')
    return
