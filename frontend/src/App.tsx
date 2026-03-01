import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider, useApp } from "./state/AppContext.tsx";
import Header from "./components/layout/Header.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import WorkspacePage from "./pages/WorkspacePage.tsx";
import AuditPage from "./pages/AuditPage.tsx";
import TrainingPage from "./pages/TrainingPage.tsx";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useApp();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function AppShell() {
  const { settings } = useApp();

  const rootClasses = [
    "flex flex-col h-screen",
    settings.highContrast ? "high-contrast" : "",
    settings.darkMode ? "dark" : "",
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
        <Route path="/" element={<ProtectedRoute><WorkspacePage /></ProtectedRoute>} />
        <Route path="/audit" element={<ProtectedRoute><AuditPage /></ProtectedRoute>} />
        <Route path="/training" element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
      </Routes>
    </div>
  );
}

function AppRoutes() {
  const { user } = useApp();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route path="/*" element={<AppShell />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <AppRoutes />
      </AppProvider>
    </BrowserRouter>
  );
}
