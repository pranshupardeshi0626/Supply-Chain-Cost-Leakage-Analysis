"""Smoke test: every page renders without an exception (uses Streamlit's AppTest)."""
import pytest
from streamlit.testing.v1 import AppTest

from app import PAGES  # noqa: F401  (import also checks the module-level code runs)

APP = str(__import__("pathlib").Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(scope="module")
def app():
    return AppTest.from_file(APP, default_timeout=180).run()


@pytest.mark.parametrize("page", list(PAGES))
def test_page_renders(app, page):
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception, [e.value for e in app.exception]


def test_empty_filter_shows_warning(app):
    app.sidebar.radio[0].set_value("Overview").run()
    app.sidebar.multiselect[0].set_value([]).run()      # no region selected
    assert any("No orders match" in w.value for w in app.warning)
