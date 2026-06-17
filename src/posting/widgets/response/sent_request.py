import httpx
from httpx import RequestNotRead
from textual.app import ComposeResult
from textual.containers import Vertical

from posting.widgets.text_area import ReadOnlyTextArea


class SentRequestTextArea(ReadOnlyTextArea):
    """
    For displaying the final request that was sent.
    """


class SentRequest(Vertical):
    def compose(self) -> ComposeResult:
        text_area = SentRequestTextArea(
            "Send a request to view the final sent request.",
            language=None,
        )
        yield text_area

    def update_request(self, request: httpx.Request) -> None:
        self.text_area.text = format_sent_request(request)

    @property
    def text_area(self) -> SentRequestTextArea:
        return self.query_one(SentRequestTextArea)


def format_sent_request(request: httpx.Request) -> str:
    headers = "\n".join(f"{name}: {value}" for name, value in request.headers.items())
    body = _format_request_body(request)

    return "\n".join(
        [
            f"{request.method} {request.url}",
            "",
            "Headers",
            headers or "(no headers)",
            "",
            "Body",
            body,
        ]
    )


def _format_request_body(request: httpx.Request) -> str:
    try:
        content = request.content
    except RequestNotRead:
        content = request.read()

    if not content:
        return "(empty body)"

    return content.decode("utf-8", errors="replace")
