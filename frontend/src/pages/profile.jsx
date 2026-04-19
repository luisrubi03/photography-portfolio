import { useEffect, useState } from "react"

function Profile() {
  const [user, setUser] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [file, setFile] = useState(null)

  useEffect(() => {
    fetch("http://localhost:5000/profile", {
      credentials: "include"
    })
      .then(res => {
        if (!res.ok) throw new Error("No auth")
        return res.json()
      })
      .then(data => {
        setUser(data)
      })
      .catch(() => setUser(null))
  }, [])

  const profilePic = user?.profile_picture
    ? `/profile_pic/${user.profile_picture}`
    : `/profile_pic/default.png`

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    const formData = new FormData()
    formData.append("imagen", file)

    try {
      const res = await fetch("http://localhost:5000/profile/edit", {
        method: "POST",
        credentials: "include",
        body: formData
      })

      const data = await res.json()

      if (data.success) {
        window.location.reload()
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (!user) return <p>Cargando perfil...</p>

  return (
    <div className="fila3">

      <div className="contenedor-texto-3">

        <div className="contenedor-textodeperfil">

          <h1 className="titulo-de-perfil">
          ¡Hola {user.user}!
          </h1>
        </div>


        <button
          onClick={() => {
            fetch("http://localhost:5000/logout", {
              method: "POST",
              credentials: "include"
            }).then(() => {
              window.location.href = "/login"
            })
          }}
          className="btn-logout"
        >
          Cerrar sesión
        </button>
        <div className="div-fdp">
          <img className="fotodeperfil"
          src={profilePic}
          style={{
            height: "100px",
            width: "100px",
            borderRadius: "50px"
          }}
          alt="profile"
        />
        </div>


        <button className="btn-editarperfil" onClick={() => setModalOpen(true)}>
          Editar perfil
        </button>

        {modalOpen && (
          <div className="modal">
            <div className="modal-content">

              <span className="onclickmodalcierre" onClick={() => setModalOpen(false)}>
                X
              </span>

              <form onSubmit={handleSubmit}>
                <label className="form-label">
                  Subir un archivo
                  <input className="inputfile" type="file" id="inputfile1"/>
                </label>


                <button type="submit">Guardar</button>
              </form>

            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default Profile