import pytest

import pyani.media.movie.create.core



@pytest.fixture
def shoot_test():
    # path to ffmpeg executable, bundled with PyShoot
    movie_generation = "C:\\PyShoot\\ffmpeg\\bin\\ffmpeg"
    # path to playback tool, using rv
    movie_playback = "C:\\Program Files\\Shotgun\RV-7.2.1\\bin\\rv"
    # enforce strict padding
    # enforce the same padding for whole image sequence
    strict_pad = True
    shoot = pyani.media.movie.create.core.AniShoot(movie_generation, movie_playback, strict_pad)
    ui = pyani.media.movie.create.core.AniShootUi()

    return shoot, ui


def test_create_full_seq(shoot_test):
    images = "C:\\Users\Patrick\\PycharmProjects\\PyShoot\\test_image_suite\\full\\"
    error, shoot_test.shoot = shoot_test.ui.process_input(images, shoot_test.shoot)
    assert not error and len(shoot_test.shoot.seq_list) == 24


def test_validate_full_seq(shoot_test):
    images = "C:\\Users\Patrick\\PycharmProjects\\PyShoot\\test_image_suite\\full\\"
    error, shoot_test.shoot = shoot_test.ui.process_input(images, shoot_test.shoot)
    error = shoot_test.ui.validate_selection(shoot_test.shoot, 3)
    assert not error


def test_validate_fail_steps_full_seq(shoot_test):
    images = "C:\\Users\Patrick\\PycharmProjects\\PyShoot\\test_image_suite\\full\\"
    error, shoot_test.shoot = shoot_test.ui.process_input(images, shoot_test.shoot)
    error = shoot_test.ui.validate_selection(shoot_test.shoot, 26)
    assert error


def test_combine_sequences(shoot_test):
    images1 = "C:\\Users\Patrick\\PycharmProjects\\PyShoot\\test_image_suite\\full\\"
    images2 = "C:\\Users\Patrick\\PycharmProjects\\PyShoot\\test_image_suite\\missing_end\\"
    images = [images1, images2]
    error, shoot_test.shoot = shoot_test.ui.process_input(images, shoot_test.shoot)
    assert not error and len(shoot_test.shoot.seq_list) == 46