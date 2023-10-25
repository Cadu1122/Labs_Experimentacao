class UnexpectedError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class SomethingException(Exception):
    def __init__(self, errors: list[dict]):
        p = []
        for e in errors:
            for message in e.get('errors', []):
                p.append(message.get('message', ''))
        p = '\n'.join(p)
        super().__init__(p)

class Unauthorized(Exception):
    ...