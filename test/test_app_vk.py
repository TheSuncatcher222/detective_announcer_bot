import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_vk import (
    define_post_topic)

from vk_wall_examples import (
    A_EXAMPLE_CHECKIN, A_EXAMPLE_GAME_RESULTS, A_EXAMPLE_OTHER,
    A_EXAMPLE_PHOTOS, A_EXAMPLE_PREVIEW, A_EXAMPLE_PRIZE_RESULTS,
    A_EXAMPLE_RATING, A_EXAMPLE_STOP_LIST, A_EXAMPLE_TASKS, A_EXAMPLE_TEAMS,
    
    D_EXAMPLE_CHECKIN, D_EXAMPLE_GAME_RESULTS, D_EXAMPLE_OTHER,
    D_EXAMPLE_PHOTOS, D_EXAMPLE_PREVIEW, D_EXAMPLE_PRIZE_RESULTS,
    D_EXAMPLE_RATING, D_EXAMPLE_STOP_LIST, D_EXAMPLE_TASKS, D_EXAMPLE_TEAMS)

def test_define_post_topic():
    post_topic_pairs: dict[dict, str] = (
        (A_EXAMPLE_CHECKIN, 'checkin'),
        (A_EXAMPLE_GAME_RESULTS, 'game_results'),
        (A_EXAMPLE_OTHER, 'other'),
        (A_EXAMPLE_PHOTOS, TypeError),
        (A_EXAMPLE_PREVIEW, 'preview'),
        (A_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
        (A_EXAMPLE_RATING, 'rating'),
        (A_EXAMPLE_STOP_LIST, TypeError),
        (A_EXAMPLE_TASKS, 'tasks'),
        (A_EXAMPLE_TEAMS, 'teams'),
        (D_EXAMPLE_CHECKIN, 'checkin'),
        (D_EXAMPLE_GAME_RESULTS, 'game_results'),
        (D_EXAMPLE_OTHER, TypeError),
        (D_EXAMPLE_PHOTOS, 'photos'),
        (D_EXAMPLE_PREVIEW, 'preview'),
        (D_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
        (D_EXAMPLE_RATING, TypeError),
        (D_EXAMPLE_STOP_LIST, 'stop-list'),
        (D_EXAMPLE_TASKS, TypeError),
        (D_EXAMPLE_TEAMS, 'teams'),)
    for post, expected in post_topic_pairs:
        try:
            assert define_post_topic(post) == expected, f'Test for {post} failed'
        except TypeError:
            # Post example is empty for now
            pass