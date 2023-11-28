from pathlib import Path

from sync import determine_actions


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {}

    actions = determine_actions(
        source_hashes,
        dest_hashes,
        Path("/src"),
        Path("/dst"),
    )

    expected_actions = [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]
    assert list(actions) == expected_actions


def test_when_a_file_has_been_renamed_in_the_source():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {"hash1": "fn2"}

    actions = determine_actions(
        source_hashes,
        dest_hashes,
        Path("/src"),
        Path("/dst"),
    )

    assert list(actions) == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]
