import pytest
from autoinst_logparse import remove_lines
from autoinst_logparse import generate_dict


@pytest.fixture
def lines():
    import os
    lines = []
    with open(os.path.join(os.getcwd(), "tests/testdata/remove_lines.txt")) as f:
        lines = f.readlines()
        f.close()
    return lines


def test_remove_lines(lines):
    filtered_lines = remove_lines(lines)
    assert len(filtered_lines) == 46


def test_generate_dict(lines):
    filtered_lines = remove_lines(lines)
    lines_dict = generate_dict(filtered_lines)
    assert len(lines_dict) == 46
    cnt_time = 0
    cnt_class = 0
    for line in lines_dict:
        assert 'msg' in line
        if 'time' in line:
            cnt_time += 1
        assert 'class' not in line
    assert cnt_time == 40
