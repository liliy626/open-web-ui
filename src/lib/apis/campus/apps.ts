import { WEBUI_API_BASE_URL } from '$lib/constants';

export type CampusAppProviderType =
	| 'native_openwebui'
	| 'ragflow_assistant'
	| 'fastgpt_app'
	| 'mcp_tool'
	| 'openapi_tool_server';

export type CampusAppDisplayMode = 'native' | 'redirect' | 'iframe';

export type CampusAgentApp = {
	id: string;
	school_id: string;
	name: string;
	description: string;
	provider_type: CampusAppProviderType;
	provider_app_id: string;
	entry_url: string;
	display_mode: CampusAppDisplayMode;
	category: string;
	category_label: string;
	icon: string;
	badge?: string | null;
	api_base_url?: string | null;
	enabled: boolean;
	sort_order: number;
	metadata: Record<string, unknown>;
};

export const getCampusApps = async (
	token: string,
	schoolId = 'yili'
): Promise<CampusAgentApp[]> => {
	let error = null;

	const query = new URLSearchParams({ school_id: schoolId });
	const res = await fetch(`${WEBUI_API_BASE_URL}/campus/apps/?${query.toString()}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err.detail ?? err.message ?? `${err}`;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
