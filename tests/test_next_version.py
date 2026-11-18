import pytest

from scripts.next_version import next_version


@pytest.mark.parametrize(
    ("latest", "release_type", "expected"),
    [
        ("v1.2.0", "minor", "v1.3.0"),
        ("v1.2.0", "patch", "v1.2.1"),
        ("v1.2.3", "major", "v2.0.0"),
        (None, "major", "v1.0.0"),
        (None, "patch", "v0.0.1"),
    ],
)
def test_next_version(latest, release_type, expected):
    assert next_version(latest, release_type) == expected


def test_rejects_unknown_tag():
    with pytest.raises(ValueError):
        next_version("release-3", "minor")
