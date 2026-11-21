import uuid

import pytest
from fastapi import HTTPException

from app.sessions import get_session_id


def test_valid_uuid_is_accepted_and_normalised():
    sid = str(uuid.uuid4())
    assert get_session_id(sid.upper()) == sid


@pytest.mark.parametrize("bad", [None, "", "not-a-uuid", "123", "../../etc/passwd"])
def test_bad_session_ids_are_rejected(bad):
    with pytest.raises(HTTPException) as err:
        get_session_id(bad)
    assert err.value.status_code == 400
