from open_webui.campus.tenants import campus_config_from_group
from open_webui.routers.campus_apps import CampusAppDisplayMode, CampusAppProviderType, get_seed_campus_apps


def test_seed_campus_apps_expose_provider_agnostic_entry_contract(monkeypatch):
    monkeypatch.delenv('RAGFLOW_API_KEY', raising=False)
    apps = get_seed_campus_apps()

    assert {app.provider_type for app in apps} >= {
        CampusAppProviderType.NATIVE_OPENWEBUI,
        CampusAppProviderType.RAGFLOW_ASSISTANT,
        CampusAppProviderType.FASTGPT_APP,
        CampusAppProviderType.MCP_TOOL,
        CampusAppProviderType.OPENAPI_TOOL_SERVER,
    }
    assert all(app.entry_url for app in apps)
    assert all(app.display_mode in set(CampusAppDisplayMode) for app in apps)


def test_seed_campus_apps_use_open_webui_group_campus_meta():
    campus = campus_config_from_group(
        type(
            'Group',
            (),
            {
                'id': 'group-meilanhu',
                'name': '美兰湖中学',
                'meta': {
                    'campus': {
                        'school_id': 'meilanhu_middle_school',
                        'ragflow': {
                            'base_url': 'http://ragflow-api.mlh.local',
                            'web_url': 'http://ragflow-web.mlh.local',
                        },
                        'fastgpt': {'entry_url': 'http://fastgpt.mlh.local'},
                    }
                },
            },
        )()
    )

    apps = get_seed_campus_apps(campus)
    knowledge = next(app for app in apps if app.provider_type == CampusAppProviderType.RAGFLOW_ASSISTANT)
    fastgpt = next(app for app in apps if app.provider_type == CampusAppProviderType.FASTGPT_APP)

    assert knowledge.entry_url == 'http://ragflow-web.mlh.local'
    assert knowledge.api_base_url == 'http://ragflow-api.mlh.local'
    assert fastgpt.entry_url == 'http://fastgpt.mlh.local'
