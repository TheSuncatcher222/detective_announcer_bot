from main import json_data_read, json_data_write

NL = '\n'

GAP: str = '      '
GAP_DASH: str = '    - '

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

    test_data = [
        {
            'key': None,
            'expected': None,
            'explanation': f'Read non-existent file error:',
            'write_data': None},
        {
            'key': 'fake_key',
            'expected': None,
            'explanation': f'Read data with wrong key error:',
            'write_data': {'keey': 'vaalue'}},
        {
            'key': None,
            'expected': {'keey': 'vaalue'},
            'explanation': f'Read existent file with data error:',
            'write_data': {'keey': 'vaalue'}},
        {
            'key': 'keey',
            'expected': 'vaalue',
            'explanation': f'Read data with correct key error:',
            'write_data': {'keey': 'vaalue'}}]
    errors: list = []
    for test in test_data:
        try:
            if test['write_data']:
                json_data_write(file_name=FILE_NAME, write_data=test['write_data'])
            test_value = json_data_read(file_name=FILE_NAME, key=test['key'])
            assert test_value == test['expected']
        except AssertionError:
            errors.append((test_value, test['expected'], test['explanation']))
    remove_file_if_exists(f'{APP_JSON_FOLDER}{FILE_NAME}')
    if not errors:
        print(f'test_json_data_read_write {GREEN_PASSED}')
    else:
        print(f'test_json_data_read_write {RED_FAILED}')
        for result, expected, explanation in errors:
            print(
                f"{GAP_DASH}{explanation}{NL}"
                f"{GAP}Expected: '{expected}'{NL}"
                f"{GAP}     Got: '{result}'")
    return
