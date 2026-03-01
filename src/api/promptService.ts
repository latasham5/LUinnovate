import apiClient from "./client.ts";
import type {
  PromptRequest,
  PromptResponse,
} from "../types/index.ts";

export async function analyzePrompt(
  request: PromptRequest,
): Promise<PromptResponse> {
  const { data } = await apiClient.post<PromptResponse>("/prompt", request);
  return data;
}

export async function getPromptHistory(): Promise<PromptResponse[]> {
  const { data } = await apiClient.get<PromptResponse[]>("/prompt/history");
  return data;
}

export async function getPromptById(
  promptId: string,
): Promise<PromptResponse> {
  const { data } = await apiClient.get<PromptResponse>(
    `/prompt/${promptId}`,
  );
  return data;
}
