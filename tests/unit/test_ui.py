from src.ui import UI


def test_ui():
    sample_user_input = "13,45"
    deposit = UI._format_deposit(sample_user_input)
    print(deposit)

    sample_user_input = "13"
    deposit = UI._format_deposit(sample_user_input)
    print(deposit)

    sample_user_input = "13,1"
    deposit = UI._format_deposit(sample_user_input)
    print(deposit)
