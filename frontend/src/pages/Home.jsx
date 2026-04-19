import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import "../App.scss"


function Home() {
  const [posts, setPosts] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    fetch("http://localhost:5000/", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        if (data.redirect) {
          navigate(data.redirect)
        } else {
          setPosts(data)
        }
      })
  }, [])

  return (
    <div className="fila">

      {/* IZQUIERDA */}
      <div className="contenedor-texto-1">
        <div className="contenedor-titulos">
          <h1 className="titulo">Popular</h1>

          <div className="feed">
            {posts.map((post, index) => (
              <div className="post" key={index}>

                {/* username */}
                <h4>{post.username}</h4>

                {/* imagen */}
                <img
                  className="upload-img"
                  src={`/static/uploads/posts/${post.filename}`}
                  alt="post"
                />

                {/* descripcion */}
                <div>
                  <p>{post.description}</p>
                </div>

              </div>
            ))}
          </div>

        </div>
      </div>

      {/* DERECHA */}
      <div className="contenedor-texto-2">
        <p className="amigos">janedoe.01</p>
        <p className="amigos">ripvanwinkle.1911</p>
        <p className="amigos">johnmilton911</p>
      </div>

    </div>
  )
}

export default Home