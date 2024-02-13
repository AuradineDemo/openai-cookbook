import asyncio
import aiohttp
import pytest
from api_request_parallel_processor import APIRequest


@pytest.fixture
def mock_session():
    class MockSession:
        async def post(self, url, headers, json):
            return {"response": "mock response"}

    return MockSession()


@pytest.fixture
def mock_retry_queue():
    class MockRetryQueue:
        def put_nowait(self, request):
            pass

    return MockRetryQueue()


@pytest.fixture
def mock_status_tracker():
    class MockStatusTracker:
        num_api_errors = 0
        num_rate_limit_errors = 0
        num_other_errors = 0
        num_tasks_in_progress = 0
        num_tasks_failed = 0
        num_tasks_succeeded = 0
        time_of_last_rate_limit_error = None

    return MockStatusTracker()


@pytest.mark.asyncio
async def test_call_api_success(mock_session, mock_retry_queue, mock_status_tracker):
    request = APIRequest(
        task_id=1,
        request_json={"input": "mock input"},
        token_consumption=1,
        attempts_left=3,
        metadata={"metadata": "mock metadata"},
    )
    await request.call_api(
        session=mock_session,
        request_url="mock url",
        request_header={"header": "mock header"},
        retry_queue=mock_retry_queue,
        save_filepath="mock filepath",
        status_tracker=mock_status_tracker,
    )
    assert request.result == [{"response": "mock response"}]
    assert mock_status_tracker.num_tasks_in_progress == 0
    assert mock_status_tracker.num_tasks_succeeded == 1


@pytest.mark.asyncio
async def test_call_api_error(mock_session, mock_retry_queue, mock_status_tracker):
    request = APIRequest(
        task_id=1,
        request_json={"input": "mock input"},
        token_consumption=1,
        attempts_left=0,
        metadata={"metadata": "mock metadata"},
    )
    await request.call_api(
        session=mock_session,
        request_url="mock url",
        request_header={"header": "mock header"},
        retry_queue=mock_retry_queue,
        save_filepath="mock filepath",
        status_tracker=mock_status_tracker,
    )
    assert request.result == ["mock error"]
    assert mock_status_tracker.num_tasks_in_progress == 0
    assert mock_status_tracker.num_tasks_failed == 1