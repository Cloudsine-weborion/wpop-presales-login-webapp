# def convert_str_to_int(value: str) -> int:
#     value = value.replace(",", "")
#     value = float(value)
#     int_value = int(value)
#     return int_value


def convert_str_to_float(value: str) -> float:
    # Remove commas and convert to float
    return float(value.replace(",", ""))


def convert_float_to_str(value: float) -> str:
    # Convert float to string with comma as thousands separator
    return "{:,.2f}".format(value)
