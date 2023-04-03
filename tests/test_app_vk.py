# Ничего не вводить
# Вводить некорректный тип данных
# Вводить невалидные данные
# Вводить неверное количество данных

from tests.vk_wall_examples import (
    EXAMPLE_CHECKIN, EXAMPLE_OTHER, EXAMPLE_PRIZE_RESULTS, EXAMPLE_PREVIEW,
    EXAMPLE_RATING, EXAMPLE_RESULTS, EXAMPLE_TEAMS)

from project.app_vk import define_post_topic


def test_define_post_topic():
    post: dict = EXAMPLE_CHECKIN
    assert define_post_topic(post) == 'checkin'
    post = EXAMPLE_OTHER
    assert define_post_topic(post) == 'other'
    post = EXAMPLE_PRIZE_RESULTS
    assert define_post_topic(post) == 'prize_results'
    post = EXAMPLE_PREVIEW
    assert define_post_topic(post) == 'preview'
    post = EXAMPLE_RATING
    assert define_post_topic(post) == 'rating'
    post = EXAMPLE_RESULTS
    assert define_post_topic(post) == 'results'
    post = EXAMPLE_TEAMS
    assert define_post_topic(post) == 'teams'

    print('test_json_data_read_write PASSED')
    return
