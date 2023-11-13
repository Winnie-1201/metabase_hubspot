// import logo from './logo.svg';
import "./App.css";

import { useEffect, useState } from "react";
export default function App() {
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const getDomainInfo = async () => {
    try {
      setLoading(true); // Set loading before sending API request
      const res = await fetch("/api");
      const response = res; // Response received
      if (!response.ok) setLoadError(await response.text());
      setLoading(false); // Stop loading
    } catch (error) {
      setLoadError(error.message);
      setLoading(false); // Stop loading in case of error
      console.error(error);
    }
  };

  useEffect(() => {
    getDomainInfo();
  }, []);

  if (loadError) {
    return (
      <div className="App">
        <h3>{loadError}</h3>
      </div>
    );
  }
  return (
    <div className="App">
      <h3>{loading ? <>Loading..</> : <>Successfully Updated!</>}</h3>
    </div>
  );
}
