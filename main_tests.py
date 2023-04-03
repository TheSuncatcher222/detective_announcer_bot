from tests import test_main, test_app_vk


def main_tests():
    test_main.test_json_data_read_write()
    test_app_vk.test_define_post_topic()
    test_app_vk.test_game_dates_add_weekday_place()
    test_app_vk.test_split_post_text()


if __name__ == '__main__':
    main_tests()
