# ABOUTME: Regression tests for Substack scheduling and scheduled release helpers.
# ABOUTME: Verifies scheduling payloads, validation, and empty response handling.

from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import Mock

from src.handlers.post_handler import PostHandler
from src.utils.api_wrapper import APIWrapper


@pytest.fixture
def mock_client():
    client = Mock()
    client.publication_url = "https://test.substack.com"
    return client


@pytest.fixture
def post_handler(mock_client):
    return PostHandler(mock_client)


@pytest.mark.asyncio
async def test_schedule_draft_uses_scheduled_release_api(post_handler, mock_client):
    scheduled_at = (
        (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=30))
        .isoformat()
        .replace("+00:00", "Z")
    )
    mock_client.get_draft.return_value = {
        "id": "draft-123",
        "draft_title": "Probe",
        "is_published": False,
        "post_date": None,
    }
    mock_client.schedule_draft.return_value = {
        "id": "draft-123",
        "postSchedules": [
            {
                "id": 1,
                "trigger_at": scheduled_at,
                "post_audience": "everyone",
                "email_audience": "everyone",
            }
        ],
    }

    result = await post_handler.schedule_draft(
        post_id="draft-123",
        scheduled_at=scheduled_at,
    )

    assert result["id"] == "draft-123"
    mock_client.schedule_draft.assert_called_once_with(
        post_id="draft-123",
        trigger_at=scheduled_at,
        post_audience="everyone",
        email_audience="everyone",
    )


@pytest.mark.asyncio
async def test_schedule_draft_rejects_past_times(post_handler, mock_client):
    mock_client.get_draft.return_value = {
        "id": "draft-123",
        "is_published": False,
        "post_date": None,
    }

    with pytest.raises(ValueError, match="must be in the future"):
        await post_handler.schedule_draft(
            post_id="draft-123",
            scheduled_at="2020-01-01T00:00:00Z",
        )


@pytest.mark.asyncio
async def test_list_scheduled_posts_filters_and_sorts(post_handler, mock_client):
    mock_client.get_drafts.return_value = [
        {
            "id": "draft-a",
            "draft_title": "Later Post",
            "postSchedules": [
                {
                    "id": 11,
                    "trigger_at": "2026-03-12T09:00:00Z",
                    "post_audience": "everyone",
                    "email_audience": "everyone",
                }
            ],
        },
        {
            "id": "draft-b",
            "draft_title": "No Schedule Yet",
            "postSchedules": [],
        },
        {
            "id": "draft-c",
            "draft_title": "Sooner Post",
            "postSchedules": [
                {
                    "id": 12,
                    "trigger_at": "2026-03-09T09:00:00Z",
                    "post_audience": "everyone",
                    "email_audience": "only_paid",
                }
            ],
        },
    ]

    scheduled = await post_handler.list_scheduled_posts(limit=10)

    assert [post["id"] for post in scheduled] == ["draft-c", "draft-a"]
    assert scheduled[0]["email_audience"] == "only_paid"
    assert scheduled[0]["scheduled_at"] == "2026-03-09T09:00:00Z"


@pytest.mark.asyncio
async def test_get_post_analytics_from_post_management(post_handler, mock_client):
    mock_client.get_post_management.return_value = {
        "posts": [
            {
                "id": "post-123",
                "title": "Analytics Probe",
                "post_date": "2026-03-01T09:00:00Z",
                "email_sent_at": "2026-03-01T09:01:00Z",
                "comment_count": 4,
                "reaction_count": 7,
                "stats": {
                    "views": 1200,
                    "sent": 800,
                    "delivered": 760,
                    "opened": 304,
                    "signups": 5,
                    "subscribes": 3,
                    "estimated_value": 42.5,
                },
            }
        ],
        "total": 1,
    }

    analytics = await post_handler.get_post_analytics("post-123")

    assert analytics["views"] == 1200
    assert analytics["delivered"] == 760
    assert analytics["opened"] == 304
    assert analytics["signups"] == 5
    assert analytics["subscribes"] == 3
    assert analytics["estimated_value"] == 42.5
    assert analytics["open_rate"] == pytest.approx(304 / 760)


def test_schedule_draft_handles_empty_success_body():
    client = Mock()
    client.publication_url = "https://test.substack.com"
    client._session = Mock()

    response = Mock()
    response.status_code = 200
    response.text = ""
    client._session.post.return_value = response

    wrapped = APIWrapper(client)
    result = wrapped.schedule_draft(
        post_id="draft-123",
        trigger_at="2026-03-27T00:15:00Z",
        post_audience="everyone",
        email_audience="everyone",
    )

    client._session.post.assert_called_once_with(
        "https://test.substack.com/drafts/draft-123/scheduled_release",
        json={
            "trigger_at": "2026-03-27T00:15:00Z",
            "post_audience": "everyone",
            "email_audience": "everyone",
        },
    )
    assert result["id"] == "draft-123"
    assert result["postSchedules"][0]["trigger_at"] == "2026-03-27T00:15:00Z"
