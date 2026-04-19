import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      const res = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
          username,
          password
        })
      });

      const result = await res.json();

      if (res.ok) {
        console.log("LOGIN OK:", result);
        navigate("/");
      } else {
        alert(result.error || "Error en login");
      }

    } catch (error) {
      console.error("ERROR REAL:", error);
      alert("Error de conexión con el servidor");
    }
  }

  return (
    <>
      <div className="contenedor-formularios">
        <div className="formulario-1">

          <div className="texto-formulario-1">
            <h2>Bienvenido de vuelta!</h2>
          </div>

          <form onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Nombre de usuario"  // 👈 importante
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <input
              type="password"
              placeholder="Contraseña"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <button type="submit">Inicia sesión</button>
          </form>

          <Link to="/register">O regístrate</Link>
          <br />
          <Link to="/recoverpassword">¿Olvidaste tu contraseña?</Link>

        </div>
      </div>
    </>
  )
}

export default Login