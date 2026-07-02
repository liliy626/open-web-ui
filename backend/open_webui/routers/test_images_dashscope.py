from types import SimpleNamespace

from open_webui.routers.images import (
    CreateImageForm,
    build_dashscope_generation_payload,
    get_dashscope_api_base_url,
    get_dashscope_image_size,
    get_dashscope_trusted_image_base_url,
    get_dashscope_task_headers,
)


def test_dashscope_api_base_url_converts_compatible_mode_url():
    assert (
        get_dashscope_api_base_url(
            'https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1'
        )
        == 'https://workspace.cn-beijing.maas.aliyuncs.com/api/v1'
    )


def test_dashscope_image_size_accepts_open_webui_and_dashscope_formats():
    assert get_dashscope_image_size('512x512') == '512*512'
    assert get_dashscope_image_size('2048*2048') == '2048*2048'
    assert get_dashscope_image_size('2k') == '2K'


def test_build_dashscope_generation_payload_uses_async_image_generation_contract():
    image_config = SimpleNamespace(
        IMAGE_SIZE='512x512',
        IMAGES_OPENAI_API_PARAMS={
            'watermark': False,
            'thinking_mode': True,
            'response_format': 'b64_json',
            '_dashscope_timeout_seconds': 9,
            '_dashscope_poll_interval_seconds': 1,
        },
    )
    form_data = CreateImageForm(
        prompt='一间有着精致窗户的花店',
        n=2,
        negative_prompt='低分辨率',
    )

    payload, timeout, poll_interval = build_dashscope_generation_payload(
        'wan2.7-image-pro',
        form_data,
        image_config,
    )

    assert timeout == 9
    assert poll_interval == 1
    assert payload == {
        'model': 'wan2.7-image-pro',
        'input': {
            'messages': [
                {
                    'role': 'user',
                    'content': [{'text': '一间有着精致窗户的花店'}],
                }
            ]
        },
        'parameters': {
            'size': '512*512',
            'n': 2,
            'negative_prompt': '低分辨率',
            'watermark': False,
            'thinking_mode': True,
        },
    }


def test_dashscope_task_headers_remove_async_submit_headers():
    assert get_dashscope_task_headers(
        {
            'Authorization': 'Bearer sk-test',
            'Content-Type': 'application/json',
            'X-DashScope-Async': 'enable',
        }
    ) == {'Authorization': 'Bearer sk-test'}


def test_dashscope_trusted_image_base_url_accepts_dashscope_oss_results():
    image_url = (
        'https://dashscope-7c2c.oss-accelerate.aliyuncs.com/path/generated.png'
        '?Expires=123&OSSAccessKeyId=test&Signature=test'
    )

    assert (
        get_dashscope_trusted_image_base_url(image_url)
        == 'https://dashscope-7c2c.oss-accelerate.aliyuncs.com'
    )


def test_dashscope_trusted_image_base_url_rejects_unexpected_hosts():
    assert get_dashscope_trusted_image_base_url('http://dashscope-7c2c.oss-accelerate.aliyuncs.com/a.png') is None
    assert get_dashscope_trusted_image_base_url('https://example.com/a.png') is None
    assert get_dashscope_trusted_image_base_url('https://dashscope.example.aliyuncs.com/a.png') is None
