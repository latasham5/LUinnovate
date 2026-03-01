import { useApp } from "../../state/AppContext.tsx";
import { AI_PLATFORMS } from "../../types/index.ts";
import type { AiPlatform } from "../../types/index.ts";

export default function PlatformSelector() {
  const { selectedPlatform, setSelectedPlatform } = useApp();

  return (
    <div className="flex items-center gap-2 px-1 mb-2">
      <label
        htmlFor="platform-select"
        className="text-xs font-medium text-gray-500 whitespace-nowrap"
      >
        Sending to:
      </label>
      <select
        id="platform-select"
        value={selectedPlatform}
        onChange={(e) => setSelectedPlatform(e.target.value as AiPlatform)}
        className="rounded-lg border border-gray-200 px-2.5 py-1 text-xs font-medium text-gray-700 focus:border-brand-red focus:ring-0 focus:outline-none"
      >
        {AI_PLATFORMS.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
    </div>
  );
}
