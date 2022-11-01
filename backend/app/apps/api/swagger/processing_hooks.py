from typing import List

Endpoint = tuple


def preprocessing_filter(endpoints: List[Endpoint]) -> List[Endpoint]:
    return [
        (path, path_regex, method, callback)
        for path, path_regex, method, callback in endpoints
        if path.startswith("/api/v")
    ]
