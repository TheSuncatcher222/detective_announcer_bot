from tests import test_main, test_app_vk
from tests.test_main import NL, YELLOW_SKIPPED


def main_tests():
    test_main.test_json_data_read_write()
    test_app_vk.test_define_post_topic()
    test_app_vk.test_game_dates_add_weekday_place()
    test_app_vk.test_get_post_image_url()
    test_app_vk.test_parse_post_photos()
    if test_app_vk.test_split_post_text():
        test_app_vk.test_parse_post_checkin()
        test_app_vk.test_parse_post_game_results()
        test_app_vk.test_parse_post_preview()
        test_app_vk.test_parse_post_stop_list()
    else:
        print(
            'Due to test_split_post_text fault next bounded tests:\n'
            f'   - test_parse_post_checkin {YELLOW_SKIPPED}{NL}'
            f'   - parse_post_game_results {YELLOW_SKIPPED}{NL}'
            f'   - test_parse_post_preview {YELLOW_SKIPPED}{NL}'
            f'   - test_parse_post_stop_list {YELLOW_SKIPPED}{NL}')


if __name__ == '__main__':
    main_tests()
