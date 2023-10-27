import json


def find_keys(
    json_data: json,
    target_key: str,
) -> list:
    """Function for finding keys in json"""
    results = []

    def find_key(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == target_key:
                    results.append(value)
                find_key(value)
        elif isinstance(data, list):
            for item in data:
                find_key(item)

    find_key(json_data)
    return results
