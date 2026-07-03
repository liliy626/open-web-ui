import pytest
from fastapi import HTTPException

from open_webui.routers.campus_knowledge import _ragflow_config


def test_ragflow_config_resolves_group_campus_meta():
    campus = {
        'school_id': 'meilanhu_middle_school',
        'ragflow': {
            'base_url': 'http://ragflow-api.mlh.local',
            'api_key': 'test-key-mlh',
            'chat_id': 'chat-mlh',
        },
    }

    assert _ragflow_config(campus) == (
        'http://ragflow-api.mlh.local',
        'test-key-mlh',
        'chat-mlh',
    )


def test_ragflow_config_requires_complete_ragflow_credentials():
    with pytest.raises(HTTPException) as exc_info:
        _ragflow_config({'school_id': 'meilanhu_middle_school', 'ragflow': {'base_url': 'http://ragflow-api.mlh.local'}})

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == 'RAGFlow is not configured: RAGFLOW_API_KEY, RAGFLOW_CHAT_ID'
