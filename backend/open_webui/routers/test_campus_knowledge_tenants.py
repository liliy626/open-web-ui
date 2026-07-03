import json

import pytest
from fastapi import HTTPException

from open_webui.routers.campus_knowledge import _ragflow_config


def test_ragflow_config_resolves_school_specific_tenant(monkeypatch):
    monkeypatch.setenv(
        'CAMPUS_TENANTS_JSON',
        json.dumps(
            {
                'meilanhu_middle_school': {
                    'name': '美兰湖中学',
                    'ragflow': {
                        'base_url': 'http://ragflow-api.mlh.local',
                        'api_key': 'test-key-mlh',
                        'chat_id': 'chat-mlh',
                    },
                },
                'gucun_first_high_school': {
                    'name': '顾村第一中学',
                    'ragflow': {
                        'base_url': 'http://ragflow-api.gucun.local',
                        'api_key': 'test-key-gucun',
                        'chat_id': 'chat-gucun',
                    },
                },
            }
        ),
    )

    assert _ragflow_config('meilanhu_middle_school') == (
        'http://ragflow-api.mlh.local',
        'test-key-mlh',
        'chat-mlh',
    )
    assert _ragflow_config('gucun_first_high_school') == (
        'http://ragflow-api.gucun.local',
        'test-key-gucun',
        'chat-gucun',
    )


def test_ragflow_config_reports_missing_school(monkeypatch):
    monkeypatch.setenv('CAMPUS_TENANTS_JSON', json.dumps({}))

    with pytest.raises(HTTPException) as exc_info:
        _ragflow_config('unknown_school')

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == 'Campus tenant is not configured: unknown_school'


def test_ragflow_config_requires_complete_ragflow_credentials(monkeypatch):
    monkeypatch.setenv(
        'CAMPUS_TENANTS_JSON',
        json.dumps(
            {
                'meilanhu_middle_school': {
                    'name': '美兰湖中学',
                    'ragflow': {
                        'base_url': 'http://ragflow-api.mlh.local',
                    },
                },
            }
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        _ragflow_config('meilanhu_middle_school')

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == 'RAGFlow is not configured: RAGFLOW_API_KEY, RAGFLOW_CHAT_ID'
