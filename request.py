from requests.sessions import Session
from requests.adapters import HTTPAdapter, Retry


def get_session():
    session = Session()

    connect = 3
    read = 3
    backoff_factor = 1
    RETRY_AFTER_STATUS_CODES = (400, 403, 500, 503)

    retry = Retry(
        total=(connect + read),
        connect=connect,
        read=read,
        backoff_factor=backoff_factor,
        status_forcelist=RETRY_AFTER_STATUS_CODES,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session