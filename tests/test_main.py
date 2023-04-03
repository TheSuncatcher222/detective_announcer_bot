from main import json_data_read, json_data_write

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
    assert test_value == 0, 'Read non-existent file FAILED.'
    
    json_data_write(file_name=FILE_NAME, write_data={'keey': 'vaalue'})
    
    test_value = None
    test_value = json_data_read(file_name=FILE_NAME, key='fake_key')
    assert test_value == 0, 'Read data with wrong key FAILED.'
    
    test_value = None
    test_value = json_data_read(file_name=None, key='keey')
    assert test_value != 'vaalue', 'Read file with correct key FAILED.'
    
    remove_file_if_exists(f'{APP_JSON_FOLDER}{FILE_NAME}')
    print('test_json_data_read_write PASSED')
    return
