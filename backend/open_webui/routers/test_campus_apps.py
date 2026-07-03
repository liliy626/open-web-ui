from open_webui.routers.campus_apps import (
    CampusAppDisplayMode,
    CampusAppProviderType,
    get_seed_campus_apps,
)


def test_seed_campus_apps_expose_provider_agnostic_entry_contract():
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


def test_seed_campus_apps_keep_provider_specific_logic_out_of_frontend_contract():
    apps = get_seed_campus_apps()

    for app in apps:
        assert app.display_mode
        assert app.entry_url
        assert app.provider_type
        assert app.enabled is True
