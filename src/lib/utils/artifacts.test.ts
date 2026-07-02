import { describe, expect, test } from 'vitest';

import { getCodeBlockContents } from './index';

describe('getCodeBlockContents artifact blocks', () => {
	test('extracts document and report artifact fences without treating them as html groups', () => {
		const result = getCodeBlockContents(`
Here is the document:

\`\`\`artifact-document
# Weekly Report

## Progress
- Drafted the plan.
\`\`\`

\`\`\`artifact-report
# Operations Summary

| Metric | Value |
| --- | --- |
| Open items | 3 |
\`\`\`
`);

		expect(result).toMatchObject({
			htmlGroups: [],
			artifacts: [
				{
					type: 'document',
					content: '# Weekly Report\n\n## Progress\n- Drafted the plan.'
				},
				{
					type: 'report',
					content: '# Operations Summary\n\n| Metric | Value |\n| --- | --- |\n| Open items | 3 |'
				}
			]
		});
	});

	test('does not promote report-like markdown responses to report artifacts', () => {
		const report = `# 美兰湖学生请假分析报告

## 一、总体情况

本报告基于学生请假系统生成，用于分析本周请假趋势、重点班级、重点学生和后续行动建议。

| 指标 | 数值 |
| --- | --- |
| 本周请假人次 | 8 |
| 上周请假人次 | 13 |

## 二、趋势对比

\`\`\`text
上周 █████████████ 13
本周 ████████ 8
\`\`\`

## 三、建议

- 关注反复请假的学生。
- 规范病假症状填写。
- 持续跟进返校健康情况。
`;

		const result = getCodeBlockContents(report);

		expect(result).toMatchObject({
			artifacts: []
		});
	});

	test('extracts explicit image artifact fences', () => {
		const result = getCodeBlockContents(`
Image result:

\`\`\`artifact-image
{"url":"/api/v1/files/image-id/content","name":"school-map.png"}
\`\`\`
`);

		expect(result).toMatchObject({
			htmlGroups: [],
			artifacts: [
				{
					type: 'image',
					content: '{"url":"/api/v1/files/image-id/content","name":"school-map.png"}'
				}
			]
		});
	});
});
