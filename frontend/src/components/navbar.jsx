import { Link } from "react-router-dom"

function Navbar({ user }) {
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
          <input type="text" placeholder="Busqueda" />

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
                src={`/static/uploads/profile_pic/${user.profile_picture}`}
              />
            )}
          </div>
        </div>

      </nav>
    </header>
  )
}

export default Navbar