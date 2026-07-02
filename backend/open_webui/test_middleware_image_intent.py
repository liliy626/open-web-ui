from open_webui.utils.middleware import has_image_edit_intent


def test_image_edit_intent_does_not_treat_new_report_image_as_edit():
    assert not has_image_edit_intent('先查找学校整体情况，再生成学校整体情况报告图片')
    assert not has_image_edit_intent('生成学校整体情况报告图片')


def test_image_edit_intent_detects_reference_image_edits():
    assert has_image_edit_intent('参考上图，把这张图改成学校整体情况报告图片')
    assert has_image_edit_intent('modify this image into a campus report poster')
