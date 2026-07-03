import json
from types import SimpleNamespace

import pytest

from open_webui.campus.tenants import (
    DEFAULT_CAMPUS_SCHOOL_ID,
    get_school_id_from_user,
    tenant_config_from_group,
    resolve_campus_tenant_config,
)


def test_school_id_resolver_prefers_explicit_value():
    user = SimpleNamespace(school_id='meilanhu_middle_school', info={'school_id': 'gucun_school'})

    assert get_school_id_from_user(user, 'explicit_school') == 'explicit_school'


def test_school_id_resolver_reads_user_info_before_default():
    user = SimpleNamespace(info={'school_id': 'meilanhu_middle_school'})

    assert get_school_id_from_user(user) == 'meilanhu_middle_school'


def test_school_id_resolver_uses_default_without_user_binding():
    user = SimpleNamespace(info={})

    assert get_school_id_from_user(user) == DEFAULT_CAMPUS_SCHOOL_ID


def test_resolve_tenant_config_from_json_env(monkeypatch):
    monkeypatch.setenv(
        'CAMPUS_TENANTS_JSON',
        json.dumps(
            {
                'meilanhu_middle_school': {
                    'name': '美兰湖中学',
                    'ragflow': {
                        'base_url': 'http://127.0.0.1:9380',
                        'api_key': 'test-meilanhu-key',
                        'chat_id': 'ragflow-chat-meilanhu',
                        'web_url': 'http://127.0.0.1:9222',
                    },
                    'fastgpt': {
                        'entry_url': 'http://127.0.0.1:3006/app/meilanhu',
                    },
                },
                'gucun_first_high_school': {
                    'name': '顾村第一中学',
                    'ragflow': {
                        'base_url': 'http://127.0.0.1:9380',
                        'api_key': 'test-gucun-key',
                        'chat_id': 'ragflow-chat-gucun',
                    },
                },
            },
            ensure_ascii=False,
        ),
    )

    tenant = resolve_campus_tenant_config('meilanhu_middle_school')

    assert tenant.school_id == 'meilanhu_middle_school'
    assert tenant.name == '美兰湖中学'
    assert tenant.ragflow is not None
    assert tenant.ragflow.chat_id == 'ragflow-chat-meilanhu'
    assert tenant.ragflow.api_key == 'test-meilanhu-key'
    assert tenant.ragflow.web_url == 'http://127.0.0.1:9222'
    assert tenant.fastgpt_entry_url == 'http://127.0.0.1:3006/app/meilanhu'


def test_tenant_config_from_open_webui_group_meta():
    group = SimpleNamespace(
        id='group-meilanhu',
        name='美兰湖中学',
        meta={
            'campus': {
                'school_id': 'meilanhu_middle_school',
                'ragflow': {
                    'base_url': 'http://ragflow-api.mlh.local',
                    'api_key': 'test-key-mlh',
                    'chat_id': 'chat-mlh',
                    'web_url': 'http://ragflow-web.mlh.local',
                },
                'fastgpt': {
                    'entry_url': 'http://fastgpt.mlh.local',
                },
            }
        },
    )

    tenant = tenant_config_from_group(group)

    assert tenant.school_id == 'meilanhu_middle_school'
    assert tenant.name == '美兰湖中学'
    assert tenant.ragflow is not None
    assert tenant.ragflow.base_url == 'http://ragflow-api.mlh.local'
    assert tenant.ragflow.chat_id == 'chat-mlh'
    assert tenant.fastgpt_entry_url == 'http://fastgpt.mlh.local'


def test_resolve_tenant_config_rejects_unknown_school(monkeypatch):
    monkeypatch.setenv('CAMPUS_TENANTS_JSON', json.dumps({}))

    with pytest.raises(KeyError):
        resolve_campus_tenant_config('unknown_school')
