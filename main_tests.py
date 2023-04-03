from tests import test_main, test_app_vk


def main_tests():
    test_main.test_json_data_read_write()
    test_app_vk.test_define_post_topic()


if __name__ == '__main__':
    main_tests()
    