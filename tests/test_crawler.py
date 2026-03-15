from gitlab_handbook_bot.crawler import is_allowed_url, normalize_url


def test_normalize_url_strips_fragment() -> None:
    assert normalize_url("https://handbook.gitlab.com/handbook/#intro") == "https://handbook.gitlab.com/handbook/"


def test_is_allowed_url_restricts_non_content_assets() -> None:
    assert is_allowed_url("https://handbook.gitlab.com/handbook/company/")
    assert not is_allowed_url("https://handbook.gitlab.com/images/logo.svg")
