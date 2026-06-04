import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Navbar({ user }) {

  const [busqueda, setBusqueda] = useState("");
  const [resultados, setResultados] = useState([]);

  const navigate = useNavigate();

  const buscarUsuarios = async (texto) => {
    setBusqueda(texto);

    if (!texto.trim()) {
      setResultados([]);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:5000/buscar?q=${encodeURIComponent(texto)}`
      );

      const data = await response.json();
      setResultados(data);

    } catch (error) {
      console.error("Error al buscar:", error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && busqueda.trim()) {
      navigate(`/search?q=${encodeURIComponent(busqueda)}`);
      setResultados([]);
    }
  };

  const profilePic = user?.profile_picture
    ? `http://localhost:5173/uploads/profile_pic/${user.profile_picture}`
    : `http://localhost:5173/uploads/profile_pic/default.png`;

  return (
    <header className="header">
      <nav className="navbar">

        <div className="nav-left">
          <span className="logo">
            <Link to="/">Rubi</Link>
          </span>
          <Link to="/">Explorar</Link>
          <Link to="#">Amigos</Link>
          <Link to="#">Mensajes</Link>
          <Link to="#">Ayuda</Link>
        </div>

        <div className="nav-right">

          <div className="search-container">
            <input
              type="text"
              placeholder="Buscar usuarios..."
              value={busqueda}
              onChange={(e) => buscarUsuarios(e.target.value)}
              onKeyDown={handleKeyDown}
            />

            {resultados.length > 0 && (
              <div className="search-results">
                {resultados.map((usuario) => (
                  <Link
                    key={usuario.id}
                    to={`/profile/${usuario.id}`}
                    className="search-result-item"
                    onClick={() => setResultados([])}
                  >
                    {usuario.username}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <span className="icon">✉</span>

          <span className="upload-text">
            <Link to="/upload">subir</Link>
          </span>

          <div className="user">
            <span>
              <Link className="user-text" to="/profile">
                {user?.username}
              </Link>
            </span>

            {user && (
              <img
                alt="user"
                src={profilePic}
              />
            )}
          </div>

        </div>

      </nav>
    </header>
  );
}

export default Navbar;