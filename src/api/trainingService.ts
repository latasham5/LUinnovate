import apiClient from "./client.ts";
import type {
  TrainingModule,
  TrainingProgress,
} from "../types/index.ts";

export async function getTrainingModules(): Promise<TrainingModule[]> {
  const { data } = await apiClient.get<TrainingModule[]>("/training");
  return data;
}

export async function getTrainingModule(
  moduleId: string,
): Promise<TrainingModule> {
  const { data } = await apiClient.get<TrainingModule>(
    `/training/${moduleId}`,
  );
  return data;
}

export async function submitTrainingResult(
  moduleId: string,
  score: number,
): Promise<TrainingProgress> {
  const { data } = await apiClient.post<TrainingProgress>(
    `/training/${moduleId}/complete`,
    { score },
  );
  return data;
}

export async function getTrainingProgress(): Promise<TrainingProgress[]> {
  const { data } = await apiClient.get<TrainingProgress[]>(
    "/training/progress",
  );
  return data;
}
