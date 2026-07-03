from __future__ import annotations

from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Depends
from open_webui.utils.auth import get_verified_user
from pydantic import BaseModel, Field

router = APIRouter()


class CampusAppProviderType(StrEnum):
    NATIVE_OPENWEBUI = 'native_openwebui'
    RAGFLOW_ASSISTANT = 'ragflow_assistant'
    FASTGPT_APP = 'fastgpt_app'
    MCP_TOOL = 'mcp_tool'
    OPENAPI_TOOL_SERVER = 'openapi_tool_server'


class CampusAppDisplayMode(StrEnum):
    NATIVE = 'native'
    REDIRECT = 'redirect'
    IFRAME = 'iframe'


class CampusAgentApp(BaseModel):
    id: str
    school_id: str = 'yili'
    name: str
    description: str
    provider_type: CampusAppProviderType
    provider_app_id: str
    entry_url: str
    display_mode: CampusAppDisplayMode
    category: str
    category_label: str
    icon: str = 'grid'
    badge: str | None = None
    api_base_url: str | None = None
    enabled: bool = True
    sort_order: int = 100
    metadata: dict[str, Any] = Field(default_factory=dict)


def get_seed_campus_apps() -> list[CampusAgentApp]:
    return [
        CampusAgentApp(
            id='campus-overview',
            name='校情总览',
            description='查看学校运行、学生动态、重点事项和本周变化。',
            provider_type=CampusAppProviderType.NATIVE_OPENWEBUI,
            provider_app_id='campus-overview',
            entry_url='/',
            display_mode=CampusAppDisplayMode.NATIVE,
            category='operations',
            category_label='校情运营',
            icon='home',
            badge='本周有变化',
            sort_order=10,
        ),
        CampusAgentApp(
            id='campus-knowledge',
            name='校园智库',
            description='连接 RAGFlow，查询制度、政策、方案、案例和问答库。',
            provider_type=CampusAppProviderType.RAGFLOW_ASSISTANT,
            provider_app_id='ragflow-campus-knowledge',
            entry_url='http://localhost:9222',
            display_mode=CampusAppDisplayMode.IFRAME,
            category='knowledge',
            category_label='知识与依据',
            icon='note',
            badge='RAGFlow',
            api_base_url='http://localhost:9380',
            sort_order=20,
        ),
        CampusAgentApp(
            id='campus-agent-flow',
            name='智能体编排',
            description='进入 FastGPT，配置校园智能体、工作流、插件和 MCP 能力。',
            provider_type=CampusAppProviderType.FASTGPT_APP,
            provider_app_id='fastgpt-campus-flow',
            entry_url='http://localhost:3006',
            display_mode=CampusAppDisplayMode.IFRAME,
            category='agents',
            category_label='智能体开发',
            icon='sparkles',
            badge='FastGPT',
            sort_order=30,
        ),
        CampusAgentApp(
            id='school-data-mcp',
            name='学校数据工具',
            description='把 PostgreSQL MCP 等结构化数据工具注册给模型使用。',
            provider_type=CampusAppProviderType.MCP_TOOL,
            provider_app_id='postgres-school-mcp',
            entry_url='/workspace/tools',
            display_mode=CampusAppDisplayMode.NATIVE,
            category='tools',
            category_label='模型工具',
            icon='component',
            badge='MCP',
            sort_order=40,
        ),
        CampusAgentApp(
            id='report-artifact-studio',
            name='报告画布',
            description='承接 PPT、图片、报告等 OpenAPI 工具输出，在 Artifacts 中预览。',
            provider_type=CampusAppProviderType.OPENAPI_TOOL_SERVER,
            provider_app_id='report-artifact-studio',
            entry_url='/apps?tool=report-artifact-studio',
            display_mode=CampusAppDisplayMode.NATIVE,
            category='creation',
            category_label='生成与画布',
            icon='document',
            badge='Artifacts',
            sort_order=50,
        ),
    ]


@router.get('/', response_model=list[CampusAgentApp])
async def get_campus_apps(school_id: str = 'yili', user=Depends(get_verified_user)):
    return sorted(
        [app for app in get_seed_campus_apps() if app.enabled and app.school_id == school_id],
        key=lambda app: app.sort_order,
    )
