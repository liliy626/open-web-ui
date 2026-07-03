import { WEBUI_API_BASE_URL } from '$lib/constants';

export type CampusKnowledgeReference = {
	id?: string | null;
	document_id?: string | null;
	document_name?: string | null;
	content?: string | null;
	similarity?: number | null;
	metadata?: Record<string, unknown> | null;
};

export type CampusKnowledgeAskResponse = {
	answer: string;
	references: CampusKnowledgeReference[];
	provider: 'ragflow';
};

export const askCampusKnowledge = async (
	token: string,
	question: string
): Promise<CampusKnowledgeAskResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/campus/knowledge/ask`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ question })
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
