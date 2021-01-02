from src.ui import UI

TEST_DATA = [
    ("13,45", 1345),
    ("13", 1300),
    ("13,1", 1310),
    ("13.45", 1345),
]


def test_ui():
    for user_input, formatted_value in TEST_DATA:
        assert UI._format_deposit(user_input) == formatted_value
