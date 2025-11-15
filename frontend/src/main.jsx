import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; //  aquí entran los estilos de Tailwind
import { Toaster } from "react-hot-toast";
<Toaster position="top-right" />
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
