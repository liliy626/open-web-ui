from types import SimpleNamespace

from open_webui.campus.tenants import (
    DEFAULT_CAMPUS_SCHOOL_ID,
    campus_config_from_group,
    env_campus_config,
    get_school_id_from_user,
)


def test_school_id_resolver_prefers_explicit_value():
    user = SimpleNamespace(info={'school_id': 'meilanhu_middle_school'})

    assert get_school_id_from_user(user, 'explicit_school') == 'explicit_school'


def test_school_id_resolver_reads_user_info_before_default():
    user = SimpleNamespace(info={'school_id': 'meilanhu_middle_school'})

    assert get_school_id_from_user(user) == 'meilanhu_middle_school'


def test_school_id_resolver_uses_default_without_user_binding():
    assert get_school_id_from_user(SimpleNamespace(info={})) == DEFAULT_CAMPUS_SCHOOL_ID


def test_campus_config_from_open_webui_group_meta():
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

    config = campus_config_from_group(group)

    assert config['school_id'] == 'meilanhu_middle_school'
    assert config['name'] == '美兰湖中学'
    assert config['ragflow']['base_url'] == 'http://ragflow-api.mlh.local'
    assert config['ragflow']['chat_id'] == 'chat-mlh'
    assert config['fastgpt']['entry_url'] == 'http://fastgpt.mlh.local'
    assert config['group_id'] == 'group-meilanhu'


def test_env_campus_config_preserves_legacy_local_env(monkeypatch):
    monkeypatch.setenv('RAGFLOW_BASE_URL', 'http://127.0.0.1:9380')
    monkeypatch.setenv('RAGFLOW_API_KEY', 'test-local-key')
    monkeypatch.setenv('RAGFLOW_CHAT_ID', 'chat-local')
    monkeypatch.setenv('RAGFLOW_WEB_URL', 'http://127.0.0.1:9222')
    monkeypatch.setenv('FASTGPT_WEB_URL', 'http://127.0.0.1:3006')

    config = env_campus_config('meilanhu_middle_school')

    assert config['school_id'] == 'meilanhu_middle_school'
    assert config['ragflow']['api_key'] == 'test-local-key'
    assert config['fastgpt']['entry_url'] == 'http://127.0.0.1:3006'
