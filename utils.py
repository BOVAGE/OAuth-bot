import httpx
from config import (
    FACEBOOK_APP_ACCESS_TOKEN,
    POLLING_INTERVAL_FOR_ACCESS_TOKEN,
    DEVICE_ACCESS_TOKEN_URL,
    DEVICE_LOGIN_CODE_URL,
)
import asyncio


async def get_device_login_codes() -> tuple[str]:
    """returns only the user_code and code to obtain access token"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DEVICE_LOGIN_CODE_URL, params={"access_token": FACEBOOK_APP_ACCESS_TOKEN}
        )
        data = resp.json()
        return (data.get("code"), data.get("user_code"))


def _handle_error_from_login_code(data_error, should_poll):
    """handle error from the login code
    it raises all errors if should_poll is set to False
    and raises all errors except PendingActionError if should_poll
    is set True"""
    api_error_to_exception = {
        1349152: "ExpiredDeviceCodeError",
        1349174: "PendingActionError",
        1349172: "PollingLimitError",
    }
    if should_poll:
        if data_error.get("error_subcode") != 1349174:
            raise Exception[data_error.get("error_subcode")]
    else:
        raise api_error_to_exception[data_error.get("error_subcode")]


async def get_access_token_from_login_code(
    code: str, should_poll: bool = False, poll_interval=0
):
    """Obtain access_token along its expiration details using the code

    NB: Polls the login status on maximum: 84 times if 5 s is used as poll interval.
    """
    # ensure poll interval isn't set when should_poll isn't True and vice versa.
    if (
        should_poll == True
        and poll_interval < POLLING_INTERVAL_FOR_ACCESS_TOKEN
        or should_poll == False
        and poll_interval > 0
    ):
        msg = (
            "Poll interval should not be set when should_poll is False and vice versa."
            f" Poll interval must be greater than or equal to {POLLING_INTERVAL_FOR_ACCESS_TOKEN}"
        )
        raise AssertionError(msg)
    async with httpx.AsyncClient() as client:
        params = {"access_token": FACEBOOK_APP_ACCESS_TOKEN, "code": code}
        resp = await client.post(DEVICE_ACCESS_TOKEN_URL, params=params)
        data = resp.json()
        if resp.status_code == 200:
            if data.get("access_token"):
                return data
            elif data.get("error"):
                _handle_error_from_login_code(data.get("error"), should_poll)
            if should_poll:
                await asyncio.sleep(poll_interval)
                return await get_access_token_from_login_code(
                    code, should_poll, poll_interval
                )
        elif resp.status_code == 400:
            if data.get("error"):
                _handle_error_from_login_code(data.get("error"), should_poll)
