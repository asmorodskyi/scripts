import pytest
from autoinst_logparse import remove_lines
from autoinst_logparse import generate_dict
from autoinst_logparse import collapse_nochange
from autoinst_logparse import remove_duplicates
from autoinst_logparse import shrink_wait_serial


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


def test_collapse_nochange():
    list_dict = [{'time': '1:1:1.1', 'msg': '1tttttttttttt'},
                 {'time': '1:1:2.1', 'msg': 'no change: 9.1s'},
                 {'time': '1:1:3.1', 'msg': 'no change: 8.1s'},
                 {'time': '1:1:5.1', 'msg': 'no match: 7.1s'},
                 {'time': '1:1:6.1', 'msg': 'no match: 6.1s'},
                 {'time': '1:1:7.1', 'msg': '2tttttttttttt'},
                 {'time': '1:1:8.1', 'msg': 'no match: 7.1s'},
                 {'time': '1:1:9.1', 'msg': '3tttttttttttt'},
                 {'time': '1:1:10.1', 'msg': '4tttttttttttt'},
                 {'time': '1:1:11.1', 'msg': 'no match: 7.1s'},
                 {'time': '1:1:12.1', 'msg': 'no match: 2.1s'},
                 {'time': '1:1:13.1', 'msg': '5tttttttttttt'}
                 ]
    expected_dict = [{'time': '1:1:1.1', 'msg': '1tttttttttttt'},
                     {'time': '1:1:2.1', 'msg': 'no match during 3.0s\n'},
                     {'time': '1:1:7.1', 'msg': '2tttttttttttt'},
                     {'time': '1:1:8.1', 'msg': 'no match during 1s\n'},
                     {'time': '1:1:9.1', 'msg': '3tttttttttttt'},
                     {'time': '1:1:10.1', 'msg': '4tttttttttttt'},
                     {'time': '1:1:11.1', 'msg': 'no match during 5.0s\n'},
                     {'time': '1:1:13.1', 'msg': '5tttttttttttt'}
                     ]
    collapsed_dict = collapse_nochange(list_dict)
    assert len(expected_dict) == 8
    for i in range(len(expected_dict)):
        assert expected_dict[i] == collapsed_dict[i]


def test_remove_duplicates():
    collapsed_dict = [{'time': '1:1:1.1', 'msg': '1tt'},
                      {'msg': '2mmm'},
                      {'time': '1:1:7.1', 'msg': '3tt'},
                      {'time': '1:1:8.1', 'msg': 'tests/yyy.pm:1 called'},
                      {'time': '1:1:9.1', 'msg': '4tt'},
                      {'time': '1:1:10.1', 'msg': 'tests/yyy.pm:1 called'},
                      {'time': '1:1:11.1', 'msg': 'tests/yyy.pm:2 called'},
                      {'time': '1:1:12.1', 'msg': 'tests/wwyy.pm:1 called'},
                      {'time': '1:1:13.1', 'msg': 'lib/wwyy.pm:1 called'},
                      {'time': '1:1:14.1', 'msg': 'lib/wwyy.pm:1 called'},
                      {'time': '1:1:15.1', 'msg': 'lib/wwyy.pm:2 called'},
                      {'time': '1:1:16.1', 'msg': 'tests/wwyy.pm:1 called'},
                      {'time': '1:1:17.1', 'msg': '5tt'},
                      {'msg': '5tt'},
                      {'msg': '5tt'}
                      ]
    nodup_dict = remove_duplicates(collapsed_dict)
    assert len(nodup_dict) == 9
    assert nodup_dict[0]['msg'] == '1tt<br/>2mmm'
    for line in nodup_dict:
        assert 'time' in line


def test_shrink_wait_serial():
    nodup = [
        {'msg': ' +++ setup notes +++', 'time': '16:15:25.0908'},
        {'msg': ' Running on openqaw...) x86_64)', 'time': '16:15:25.0908'},
        {'msg': ' testapi::script_run(cmd="systemctl enable serial-getty\\@hvc1; systemctl start serial-getty\\@hvc1", output="", quiet=1, timeout=undef)', 'time': '16:17:07.421'},
        {'msg': ' testapi::wait_serial(quiet=1, regexp="# ", timeout=90, expect_not_found=0, no_regex=1, buffer_size=undef, record_output=undef)', 'time': '16:17:07.828'},
        {'msg': 'testapi::wait_serial: # : ok', 'time': '16:17:07.422'},
        {'msg': ' Running on openqaw...) x86_64)', 'time': '16:15:25.0908'},
        {'msg': ' testapi::wait_serial(quiet=1, regexp="# ", timeout=90, expect_not_found=0, record_output=undef, no_regex=1, buffer_size=undef)', 'time': '16:17:07.836'},
        {'msg': ' testapi::wait_serial: # : ok', 'time': '16:17:07.837'},
        {'msg': ' +++ setup notes +++', 'time': '16:15:25.0908'}
    ]
    shrinked = shrink_wait_serial(nodup)
    assert len(shrinked) == 7
    for line in shrinked:
        assert 'testapi::wait_serial: # : ok' not in line['msg']
