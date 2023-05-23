import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from project.app_vk import (
    define_post_topic, )

from vk_wall_examples import (
    A_EXAMPLE_CHECKIN, A_EXAMPLE_GAME_RESULTS, A_EXAMPLE_OTHER,
    A_EXAMPLE_PHOTOS, A_EXAMPLE_PREVIEW, A_EXAMPLE_PRIZE_RESULTS,
    A_EXAMPLE_RATING, A_EXAMPLE_STOP_LIST, A_EXAMPLE_TASKS, A_EXAMPLE_TEAMS,

    D_EXAMPLE_CHECKIN, D_EXAMPLE_GAME_RESULTS, D_EXAMPLE_OTHER,
    D_EXAMPLE_PHOTOS, D_EXAMPLE_PREVIEW, D_EXAMPLE_PRIZE_RESULTS,
    D_EXAMPLE_RATING, D_EXAMPLE_STOP_LIST, D_EXAMPLE_TASKS, D_EXAMPLE_TEAMS)


@pytest.mark.parametrize('post_example, expected_topic', [
    (A_EXAMPLE_CHECKIN, 'checkin'),
    (A_EXAMPLE_GAME_RESULTS, 'game_results'),
    (A_EXAMPLE_OTHER, 'other'),
    # (A_EXAMPLE_PHOTOS, TypeError),
    (A_EXAMPLE_PREVIEW, 'preview'),
    (A_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    (A_EXAMPLE_RATING, 'rating'),
    # (A_EXAMPLE_STOP_LIST, TypeError),
    (A_EXAMPLE_TASKS, 'tasks'),
    (A_EXAMPLE_TEAMS, 'teams'),
    (D_EXAMPLE_CHECKIN, 'checkin'),
    (D_EXAMPLE_GAME_RESULTS, 'game_results'),
    # (D_EXAMPLE_OTHER, TypeError),
    (D_EXAMPLE_PHOTOS, 'photos'),
    (D_EXAMPLE_PREVIEW, 'preview'),
    (D_EXAMPLE_PRIZE_RESULTS, 'prize_results'),
    # (D_EXAMPLE_RATING, TypeError),
    (D_EXAMPLE_STOP_LIST, 'stop-list'),
    # (D_EXAMPLE_TASKS, TypeError),
    (D_EXAMPLE_TEAMS, 'teams'),
])
def test_define_post_topic(post_example, expected_topic) -> None:
    """Test define_post_topic func from app_vk."""
    assert define_post_topic(post_example) == expected_topic


@pytest.mark.skip(reason='Currently no way to test it!')
def test_init_vk_bot() -> None:
    """Test init_vk_bot func from app_vk."""
    pass
