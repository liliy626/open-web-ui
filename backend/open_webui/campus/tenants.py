from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, Field, ValidationError

DEFAULT_CAMPUS_SCHOOL_ID = 'meilanhu_middle_school'


class CampusRagFlowTenantConfig(BaseModel):
    base_url: str = 'http://localhost:9380'
    api_key: str | None = None
    chat_id: str | None = None
    web_url: str = 'http://localhost:9222'

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.chat_id)


class CampusTenantConfig(BaseModel):
    school_id: str
    name: str
    ragflow: CampusRagFlowTenantConfig | None = None
    fastgpt_entry_url: str = 'http://localhost:3006'
    metadata: dict[str, Any] = Field(default_factory=dict)


def get_school_id_from_user(user: Any | None, requested_school_id: str | None = None) -> str:
    if requested_school_id:
        return requested_school_id

    user_school_id = _get_user_school_id(user)
    if user_school_id:
        return user_school_id

    return DEFAULT_CAMPUS_SCHOOL_ID


async def resolve_campus_tenant_config_for_user(
    user: Any | None,
    requested_school_id: str | None = None,
    db: Any | None = None,
) -> CampusTenantConfig:
    if requested_school_id:
        return resolve_campus_tenant_config(requested_school_id)

    user_school_id = _get_user_school_id(user)
    if user_school_id:
        return resolve_campus_tenant_config(user_school_id)

    group_tenant = await _resolve_campus_tenant_from_user_groups(user, db)
    if group_tenant:
        return group_tenant

    return resolve_campus_tenant_config(DEFAULT_CAMPUS_SCHOOL_ID)


def _get_user_school_id(user: Any | None) -> str | None:
    user_school_id = getattr(user, 'school_id', None)
    if isinstance(user_school_id, str) and user_school_id.strip():
        return user_school_id.strip()

    user_info = getattr(user, 'info', None)
    if isinstance(user_info, dict):
        info_school_id = user_info.get('school_id')
        if isinstance(info_school_id, str) and info_school_id.strip():
            return info_school_id.strip()

    return None


async def _resolve_campus_tenant_from_user_groups(user: Any | None, db: Any | None) -> CampusTenantConfig | None:
    user_id = getattr(user, 'id', None)
    if not user_id:
        return None

    from open_webui.models.groups import Groups

    groups = await Groups.get_groups(filter={'member_id': user_id}, db=db)
    for group in groups:
        group_meta = getattr(group, 'meta', None) or {}
        if isinstance(group_meta, dict) and isinstance(group_meta.get('campus'), dict):
            return tenant_config_from_group(group)

    return None


def resolve_campus_tenant_config(school_id: str | None = None) -> CampusTenantConfig:
    resolved_school_id = school_id or DEFAULT_CAMPUS_SCHOOL_ID
    registry = _load_tenant_registry()

    if resolved_school_id not in registry:
        raise KeyError(f'Campus tenant is not configured: {resolved_school_id}')

    return registry[resolved_school_id]


def tenant_config_from_group(group: Any) -> CampusTenantConfig:
    group_meta = getattr(group, 'meta', None) or {}
    if not isinstance(group_meta, dict):
        raise ValueError('Open WebUI group meta must be an object')

    campus_meta = group_meta.get('campus') or {}
    if not isinstance(campus_meta, dict):
        raise ValueError('Open WebUI group meta.campus must be an object')

    school_id = campus_meta.get('school_id') or getattr(group, 'id', None)
    if not isinstance(school_id, str) or not school_id.strip():
        raise ValueError('Open WebUI group campus config requires school_id')

    payload = {
        'name': campus_meta.get('name') or getattr(group, 'name', None) or school_id,
        'ragflow': campus_meta.get('ragflow'),
        'fastgpt': campus_meta.get('fastgpt') or {},
        'metadata': {
            **campus_meta.get('metadata', {}),
            'open_webui_group_id': getattr(group, 'id', None),
        },
    }
    return _tenant_config_from_dict(school_id.strip(), payload)


def _load_tenant_registry() -> dict[str, CampusTenantConfig]:
    raw_registry = os.getenv('CAMPUS_TENANTS_JSON', '').strip()
    if raw_registry:
        return _parse_tenant_registry_json(raw_registry)

    return {
        DEFAULT_CAMPUS_SCHOOL_ID: _legacy_default_tenant_config(),
    }


def _parse_tenant_registry_json(raw_registry: str) -> dict[str, CampusTenantConfig]:
    try:
        parsed = json.loads(raw_registry)
    except json.JSONDecodeError as exc:
        raise ValueError('CAMPUS_TENANTS_JSON must be a valid JSON object') from exc

    if not isinstance(parsed, dict):
        raise ValueError('CAMPUS_TENANTS_JSON must be a JSON object keyed by school_id')

    tenants: dict[str, CampusTenantConfig] = {}
    for school_id, value in parsed.items():
        if not isinstance(school_id, str) or not isinstance(value, dict):
            raise ValueError('CAMPUS_TENANTS_JSON entries must be objects keyed by string school_id')

        tenants[school_id] = _tenant_config_from_dict(school_id, value)

    return tenants


def _tenant_config_from_dict(school_id: str, value: dict[str, Any]) -> CampusTenantConfig:
    fastgpt_value = value.get('fastgpt') or {}
    if not isinstance(fastgpt_value, dict):
        raise ValueError(f'Campus tenant fastgpt config must be an object: {school_id}')

    payload = {
        'school_id': school_id,
        'name': value.get('name') or school_id,
        'ragflow': value.get('ragflow'),
        'fastgpt_entry_url': fastgpt_value.get('entry_url') or value.get('fastgpt_entry_url') or 'http://localhost:3006',
        'metadata': value.get('metadata') or {},
    }

    try:
        return CampusTenantConfig.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f'Invalid campus tenant config: {school_id}') from exc


def _legacy_default_tenant_config() -> CampusTenantConfig:
    ragflow = CampusRagFlowTenantConfig(
        base_url=os.getenv('RAGFLOW_BASE_URL', 'http://localhost:9380').strip().rstrip('/'),
        api_key=os.getenv('RAGFLOW_API_KEY', '').strip() or None,
        chat_id=os.getenv('RAGFLOW_CHAT_ID', '').strip() or None,
        web_url=os.getenv('RAGFLOW_WEB_URL', 'http://localhost:9222').strip().rstrip('/'),
    )

    return CampusTenantConfig(
        school_id=DEFAULT_CAMPUS_SCHOOL_ID,
        name=os.getenv('CAMPUS_DEFAULT_SCHOOL_NAME', '美兰湖中学').strip() or '美兰湖中学',
        ragflow=ragflow,
        fastgpt_entry_url=os.getenv('FASTGPT_WEB_URL', 'http://localhost:3006').strip().rstrip('/'),
    )
