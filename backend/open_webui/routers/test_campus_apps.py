import json

from open_webui.routers.campus_apps import CampusAppDisplayMode, CampusAppProviderType, get_seed_campus_apps


def test_seed_campus_apps_expose_provider_agnostic_entry_contract(monkeypatch):
    monkeypatch.delenv('CAMPUS_TENANTS_JSON', raising=False)

    apps = get_seed_campus_apps('meilanhu_middle_school')

    assert {app.provider_type for app in apps} >= {
        CampusAppProviderType.NATIVE_OPENWEBUI,
        CampusAppProviderType.RAGFLOW_ASSISTANT,
        CampusAppProviderType.FASTGPT_APP,
        CampusAppProviderType.MCP_TOOL,
        CampusAppProviderType.OPENAPI_TOOL_SERVER,
    }
    assert all(app.entry_url for app in apps)
    assert all(app.display_mode in set(CampusAppDisplayMode) for app in apps)


def test_seed_campus_apps_keep_provider_specific_logic_out_of_frontend_contract(monkeypatch):
    monkeypatch.delenv('CAMPUS_TENANTS_JSON', raising=False)

    apps = get_seed_campus_apps('meilanhu_middle_school')

    for app in apps:
        assert app.display_mode
        assert app.entry_url
        assert app.provider_type
        assert app.enabled is True


def test_seed_campus_apps_use_school_specific_provider_urls(monkeypatch):
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
                        'web_url': 'http://ragflow-web.mlh.local',
                    },
                    'fastgpt': {'entry_url': 'http://fastgpt.mlh.local'},
                },
                'gucun_first_high_school': {
                    'name': '顾村第一中学',
                    'ragflow': {
                        'base_url': 'http://ragflow-api.gucun.local',
                        'api_key': 'test-key-gucun',
                        'chat_id': 'chat-gucun',
                        'web_url': 'http://ragflow-web.gucun.local',
                    },
                    'fastgpt': {'entry_url': 'http://fastgpt.gucun.local'},
                },
            }
        ),
    )

    meilanhu_apps = get_seed_campus_apps('meilanhu_middle_school')
    gucun_apps = get_seed_campus_apps('gucun_first_high_school')

    meilanhu_knowledge = next(app for app in meilanhu_apps if app.provider_type == CampusAppProviderType.RAGFLOW_ASSISTANT)
    gucun_knowledge = next(app for app in gucun_apps if app.provider_type == CampusAppProviderType.RAGFLOW_ASSISTANT)
    meilanhu_fastgpt = next(app for app in meilanhu_apps if app.provider_type == CampusAppProviderType.FASTGPT_APP)
    gucun_fastgpt = next(app for app in gucun_apps if app.provider_type == CampusAppProviderType.FASTGPT_APP)

    assert meilanhu_knowledge.entry_url == 'http://ragflow-web.mlh.local'
    assert meilanhu_knowledge.api_base_url == 'http://ragflow-api.mlh.local'
    assert gucun_knowledge.entry_url == 'http://ragflow-web.gucun.local'
    assert gucun_knowledge.api_base_url == 'http://ragflow-api.gucun.local'
    assert meilanhu_fastgpt.entry_url == 'http://fastgpt.mlh.local'
    assert gucun_fastgpt.entry_url == 'http://fastgpt.gucun.local'
