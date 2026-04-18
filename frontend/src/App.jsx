import { useEffect, useState } from "react"
import "./App.scss"

function App() {
  const [showNavbar, setShowNavbar] = useState(true)
  const [user, setUser] = useState(null)

  // Simulación de obtener datos del backend (Flask API)
  useEffect(() => {
    fetch("/api/user")
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => {
        // fallback si no hay backend aún
        setUser({
          username: "Ruby_user",
          profile_picture: "default.png"
        })
      })
  }, [])

  return (
    <>
      {showNavbar && (
        <header className="header">
          <nav className="navbar">

            {/* LEFT */}
            <div className="nav-left">
              <span className="logo">
                <a href="/">Rubi</a>
              </span>
              <a href="#">Explorar</a>
              <a href="#">Amigos</a>
              <a href="#">Mensajes</a>
              <a href="#">Ayuda</a>
            </div>

            {/* RIGHT */}
            <div className="nav-right">
              <input type="text" placeholder="Busqueda" />

              <span className="icon">✉</span>

              <span className="upload-text">
                <a href="/upload">subir</a>
              </span>

              <div className="user">
                <span>
                  <a className="user-text" href="/profile">
                    {user?.username}
                  </a>
                </span>

                {user && (
                  <img
                    alt="user"
                    src={`/uploads/profile_pic/${user.profile_picture}`}
                  />
                )}
              </div>
            </div>
          </nav>
        </header>
      )}

      <main>
        <h1>Contenido principal</h1>
        <p>Aquí iría lo que antes ponías en {% block content %}</p>
      </main>
    </>
  )
}

export default App