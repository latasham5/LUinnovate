# PromptGuard Agent – AI Safety Layer

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

## Demo Walkthrough

### 1. Safe Message
1. Navigate to **Workspace** (`/`)
2. Type: `Can you help me summarize our quarterly revenue trends?`
3. Click **Send** or press **Enter**
4. Observe: PromptGuard Agent panel shows **Safe** status, message sends normally

### 2. Flagged Message
1. Type: `Send the report to john.doe@company.com, his SSN is 123-45-6789`
2. Click **Send**
3. Observe: PromptGuard **intercepts** the message with a modal dialog
4. The dialog shows:
   - **High Risk** severity badge
   - **PII** category chip
   - Explanation of why it was flagged
   - A safer rewrite with email and SSN replaced by placeholders

### 3. Safer Rewrite
1. In the intercept dialog, optionally edit the safer prompt
2. Click **Use safer prompt**
3. Observe: The rewritten message is sent with a green "Rewritten by PromptGuard" label
4. The agent panel updates with the flagged event

### 4. Audit Log
1. Navigate to **Audit** (`/audit`)
2. Review KPI cards (Total, Flagged, High Risk)
3. Use the category/severity filters
4. Click **View** on any row to see the detail drawer
5. Click **Export CSV** to download the filtered audit log

### 5. Training Trigger
1. Send 3 or more flagged/rewritten messages in the Workspace
2. Observe the **Training Required** banner in the agent panel
3. Navigate to **Training** (`/training`)
4. Answer all 3 scenarios and submit
5. On all correct: **Training completed** banner appears

## Accessibility

- Skip to main content link
- Full keyboard navigation with visible focus rings
- `aria-live` regions for safety announcements
- Accessible modal dialog with focus trap + ESC to close
- Text size toggle (S/M/L) and high contrast mode
- `prefers-reduced-motion` respected
- Semantic HTML throughout (header, nav, main, section, table, fieldset)
- Color is never the sole indicator — text labels + icons accompany all risk levels

## Design Principles

- Clean white background with soft gray borders
- Primary accent `#F40009` used sparingly (primary buttons, critical alerts)
- Rounded corners (12-16px), subtle shadows
- Professional enterprise tone — no playful gradients or flashy UI
- Feels like a familiar chat interface with a built-in safety layer
