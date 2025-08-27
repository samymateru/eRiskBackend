import uuid
from contextlib import contextmanager
from fastapi import HTTPException
from enum import Enum



def get_unique_key():
    uuid_str = str(uuid.uuid4()).split("-")
    key = uuid_str[0] + uuid_str[1]
    return key


def from_enum(data: Enum):
    return data.value

@contextmanager
def exception_response():
    """
    Context manager for standardized exception handling in FastAPI routes or logic blocks.

    This context manager catches unhandled exceptions within the enclosed block and converts
    them into standardized HTTP 500 responses using FastAPI's HTTPException. If an HTTPException
    is raised within the block, it is re-raised and handled as-is, allowing custom error handling
    to pass through.

    This is useful for centralizing error handling logic when writing reusable components,
    background tasks, or route functions where consistent error formatting is desired.

    Raises:
        HTTPException: Re-raises any caught HTTPException unchanged.
        HTTPException: Raises a 500 Internal Server Error for any other unhandled exception,
                       with the original error message included in the response detail.
    """
    try:
        yield

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
