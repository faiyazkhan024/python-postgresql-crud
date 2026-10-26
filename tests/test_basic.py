"""Smoke test for application imports and basic sanity checks."""

import python_postgresql_crud


def test_package_metadata() -> None:
    """Verify package can be imported and executed without errors."""
    assert hasattr(python_postgresql_crud, "main")
