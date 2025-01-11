import pytest
from database.interface import NoSqlDb

def test_abstract_methods():
    """Ensure NoSqlDb cannot be instantiated and enforces method implementation."""
    with pytest.raises(TypeError):
        NoSqlDb()  # Should fail since it's an abstract class
