import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { CarCreatePage } from "./pages/CarCreatePage";
import { CarDetailPage } from "./pages/CarDetailPage";
import { CarsListPage } from "./pages/CarsListPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/cars" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/cars" element={<CarsListPage />} />
          <Route path="/cars/new" element={<CarCreatePage />} />
          <Route path="/cars/:id" element={<CarDetailPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/cars" replace />} />
    </Routes>
  );
}

export default App;
