import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider, useApp } from "./state/AppContext.tsx";
import Header from "./components/layout/Header.tsx";
import WorkspacePage from "./pages/WorkspacePage.tsx";
import AuditPage from "./pages/AuditPage.tsx";
import TrainingPage from "./pages/TrainingPage.tsx";

function AppShell() {
  const { settings } = useApp();

  const rootClasses = [
    "flex flex-col h-screen",
    settings.highContrast ? "high-contrast" : "",
    `text-size-${settings.textSize}`,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={rootClasses}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Header />
      <Routes>
        <Route path="/" element={<WorkspacePage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/training" element={<TrainingPage />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <AppShell />
      </AppProvider>
    </BrowserRouter>
  );
}
