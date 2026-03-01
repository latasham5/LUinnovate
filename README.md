# S.I.P Agent – AI Safety Layer

A team-based software development project collaborated with multiple developers to design, build, test, and deploy software used for an organized process.

An enterprise-grade React frontend for an AI safety agent that integrates into existing AI tools (ChatGPT Enterprise, Microsoft Copilot, etc.) as a guardrail layer. It intercepts, analyzes, and rewrites prompts containing sensitive data before they reach any AI model.

## Tech Stack

- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS v4** (styling)
- **React Router v6** (client-side routing)
- **Lucide React** (icons)

No heavy UI libraries. Minimal dependencies.

## Getting Started

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

The app runs at `http://localhost:5173` by default.

## Environment Variables

The app currently runs in **mock mode** with simulated API responses. To connect to a real backend, create a `.env` file:

```env
VITE_API_MODE=mock        # "mock" (default) or "live"
VITE_API_BASE_URL=         # Base URL for real backend (when mode is "live")
```

The mock layer is in `src/api/mock.ts`. Replace with real HTTP calls in a production integration.

## Project Structure

```
src/
  api/              # API layer (mock + real backend toggle)
    index.ts        # Re-exports (swap mock/live here)
    mock.ts         # Mock API with artificial latency
  components/
    audit/          # Audit page components (KPIs, filters, chart, table)
    common/         # Shared components (status badges, chips)
    layout/         # Header, navigation
    workspace/      # Chat area, composer, agent panel, intercept dialog
    training/       # (reserved)
  hooks/            # Custom hooks (focus trap)
  pages/            # Route-level page components
  state/            # React Context (global app state)
  types/            # TypeScript type definitions
  utils/            # Detection engine, CSV export, ID generator
```
