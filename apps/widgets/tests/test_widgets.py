import pytest
from widgets.main import main

def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert "Welcome to widgets!" in captured.out
