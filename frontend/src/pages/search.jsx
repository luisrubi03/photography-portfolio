import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";


function Search() {

  const [searchParams] = useSearchParams();
  const [resultados, setResultados] = useState([]);

  const q = searchParams.get("q");

  useEffect(() => {

    const cargarResultados = async () => {

      const res = await fetch(
        `http://localhost:5000/search?q=${encodeURIComponent(q)}`
      );

      const data = await res.json();
      setResultados(data);
    };

    if (q) {
      cargarResultados();
    }

  }, [q]);

  return (
    <div className="search-page">
      <h2>Resultados para "{q}"</h2>

      {resultados.map((usuario) => (
        <div key={usuario.id}>
          <h3>{usuario.username}</h3>
        </div>
      ))}
    </div>
  );
}

export default Search;