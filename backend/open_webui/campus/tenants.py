from __future__ import annotations

import os
from typing import Any

DEFAULT_CAMPUS_SCHOOL_ID = 'meilanhu_middle_school'


def get_school_id_from_user(user: Any | None, requested_school_id: str | None = None) -> str:
    if requested_school_id:
        return requested_school_id

    user_info = getattr(user, 'info', None)
    if isinstance(user_info, dict) and isinstance(user_info.get('school_id'), str) and user_info['school_id'].strip():
        return user_info['school_id'].strip()

    return DEFAULT_CAMPUS_SCHOOL_ID


def campus_config_from_group(group: Any) -> dict[str, Any]:
    meta = getattr(group, 'meta', None) or {}
    campus = meta.get('campus') if isinstance(meta, dict) else None
    if not isinstance(campus, dict):
        raise ValueError('Open WebUI group meta.campus must be an object')

    school_id = campus.get('school_id') or getattr(group, 'id', DEFAULT_CAMPUS_SCHOOL_ID)
    fastgpt = campus.get('fastgpt') if isinstance(campus.get('fastgpt'), dict) else {}

    return {
        'school_id': str(school_id).strip(),
        'name': campus.get('name') or getattr(group, 'name', str(school_id)),
        'group_id': getattr(group, 'id', None),
        'ragflow': campus.get('ragflow') if isinstance(campus.get('ragflow'), dict) else {},
        'fastgpt': {'entry_url': fastgpt.get('entry_url') or 'http://localhost:3006'},
    }


def env_campus_config(school_id: str = DEFAULT_CAMPUS_SCHOOL_ID) -> dict[str, Any]:
    return {
        'school_id': school_id,
        'name': os.getenv('CAMPUS_DEFAULT_SCHOOL_NAME', '美兰湖中学').strip() or '美兰湖中学',
        'ragflow': {
            'base_url': os.getenv('RAGFLOW_BASE_URL', 'http://localhost:9380').strip().rstrip('/'),
            'api_key': os.getenv('RAGFLOW_API_KEY', '').strip(),
            'chat_id': os.getenv('RAGFLOW_CHAT_ID', '').strip(),
            'web_url': os.getenv('RAGFLOW_WEB_URL', 'http://localhost:9222').strip().rstrip('/'),
        },
        'fastgpt': {
            'entry_url': os.getenv('FASTGPT_WEB_URL', 'http://localhost:3006').strip().rstrip('/'),
        },
    }


async def get_campus_config_for_user(
    user: Any | None,
    requested_school_id: str | None = None,
    db: Any | None = None,
) -> dict[str, Any]:
    if requested_school_id:
        return env_campus_config(requested_school_id)

    user_id = getattr(user, 'id', None)
    if user_id:
        from open_webui.models.groups import Groups

        groups = await Groups.get_groups(filter={'member_id': user_id}, db=db)
        for group in groups:
            meta = getattr(group, 'meta', None) or {}
            if isinstance(meta, dict) and isinstance(meta.get('campus'), dict):
                return campus_config_from_group(group)

    return env_campus_config(get_school_id_from_user(user))
