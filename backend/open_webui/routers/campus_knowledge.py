from __future__ import annotations

import logging
from typing import Any

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, status
from open_webui.campus.tenants import (
    CampusTenantConfig,
    get_school_id_from_user,
    resolve_campus_tenant_config,
    resolve_campus_tenant_config_for_user,
)
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL, AIOHTTP_CLIENT_TIMEOUT
from open_webui.internal.db import get_async_session
from open_webui.utils.auth import get_verified_user
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

router = APIRouter()


class CampusKnowledgeAskForm(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[dict[str, str]] = Field(default_factory=list)
    school_id: str | None = None


class CampusKnowledgeReference(BaseModel):
    id: str | None = None
    document_id: str | None = None
    document_name: str | None = None
    content: str | None = None
    similarity: float | None = None
    metadata: dict[str, Any] | None = None


class CampusKnowledgeAskResponse(BaseModel):
    answer: str
    references: list[CampusKnowledgeReference]
    provider: str = 'ragflow'


def _ragflow_config(school_id: str) -> tuple[str, str, str]:
    try:
        tenant = resolve_campus_tenant_config(school_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Campus tenant is not configured: {school_id}',
        ) from exc

    return _ragflow_config_from_tenant(tenant)


def _ragflow_config_from_tenant(tenant: CampusTenantConfig) -> tuple[str, str, str]:
    ragflow = tenant.ragflow
    base_url = ragflow.base_url.strip().rstrip('/') if ragflow else ''
    api_key = ragflow.api_key.strip() if ragflow and ragflow.api_key else ''
    chat_id = ragflow.chat_id.strip() if ragflow and ragflow.chat_id else ''

    missing = [
        name
        for name, value in (
            ('RAGFLOW_BASE_URL', base_url),
            ('RAGFLOW_API_KEY', api_key),
            ('RAGFLOW_CHAT_ID', chat_id),
        )
        if not value
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'RAGFlow is not configured: {", ".join(missing)}',
        )

    return base_url, api_key, chat_id


def _normalize_references(reference: dict[str, Any] | None) -> list[CampusKnowledgeReference]:
    if not reference:
        return []

    chunks = reference.get('chunks') or {}
    normalized: list[CampusKnowledgeReference] = []
    for chunk_id, chunk in chunks.items():
        if not isinstance(chunk, dict):
            continue

        normalized.append(
            CampusKnowledgeReference(
                id=str(chunk.get('id') or chunk_id),
                document_id=chunk.get('document_id'),
                document_name=chunk.get('document_name'),
                content=chunk.get('content'),
                similarity=chunk.get('similarity'),
                metadata=chunk.get('document_metadata'),
            )
        )

    return normalized


def _build_messages(question: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
    messages = [
        message
        for message in history
        if message.get('role') in {'user', 'assistant', 'system'} and isinstance(message.get('content'), str)
    ]
    messages.append({'role': 'user', 'content': question})
    return messages


@router.get('/status')
async def get_campus_knowledge_status(
    school_id: str | None = None,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    resolved_school_id = get_school_id_from_user(user, school_id)
    try:
        tenant = await resolve_campus_tenant_config_for_user(user, school_id, db=db)
    except KeyError:
        return {
            'provider': 'ragflow',
            'school_id': resolved_school_id,
            'configured': False,
            'base_url': '',
            'chat_id': '',
        }

    resolved_school_id = tenant.school_id
    ragflow = tenant.ragflow
    base_url = ragflow.base_url if ragflow else ''
    api_key = ragflow.api_key if ragflow and ragflow.api_key else ''
    chat_id = ragflow.chat_id if ragflow and ragflow.chat_id else ''

    return {
        'provider': 'ragflow',
        'school_id': resolved_school_id,
        'configured': bool(base_url and api_key and chat_id),
        'base_url': base_url,
        'chat_id': chat_id,
    }


@router.post('/ask', response_model=CampusKnowledgeAskResponse)
async def ask_campus_knowledge(
    form_data: CampusKnowledgeAskForm,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    school_id = get_school_id_from_user(user, form_data.school_id)
    try:
        tenant = await resolve_campus_tenant_config_for_user(user, form_data.school_id, db=db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Campus tenant is not configured: {school_id}',
        ) from exc
    base_url, api_key, chat_id = _ragflow_config_from_tenant(tenant)

    payload = {
        'model': 'model',
        'messages': _build_messages(form_data.question, form_data.history),
        'stream': False,
        'extra_body': {
            'reference': True,
            'reference_metadata': {'include': True},
        },
    }

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_CLIENT_TIMEOUT)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    url = f'{base_url}/api/v1/openai/{chat_id}/chat/completions'
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        async with session.post(url, json=payload, headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL) as response:
            response_payload = await response.json(content_type=None)
            if response.status >= 400:
                message = response_payload.get('message') or response_payload.get('detail') or response.reason
                raise HTTPException(status_code=response.status, detail=message)

    choices = response_payload.get('choices') or []
    if not choices:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='RAGFlow returned no choices',
        )

    message = choices[0].get('message') or {}
    answer = message.get('content') or ''
    references = _normalize_references(message.get('reference'))

    return CampusKnowledgeAskResponse(answer=answer, references=references)
