import pytest
from backend2.main import main

def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert "Welcome to backend2!" in captured.out
