import { useState } from "react"
import { Link } from "react-router-dom"

function Profile({ username }) {
  const [modalOpen, setModalOpen] = useState(false)
  const [file, setFile] = useState(null)

  const openModal = () => setModalOpen(true)
  const closeModal = () => setModalOpen(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }
  const profilePic =
  username?.profile_picture
    ? `/profile_pic/${username1.profile_picture}`
    : `/profile_pic/default.png`

  const userName = username?.user["username"]
  if (!username){
    userName = "John Doe"
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
        alert("Perfil actualizado")
        window.location.reload()
      } else {
        alert("Error al actualizar")
      }
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="fila3">

      <div className="contenedor-texto-3">

        <div className="contenedor-titulos3">
          <h1 className="titulo">
            ¡Hola {userName}!
          </h1>

          <button
            onClick={() => {
              fetch("http://localhost:5000/logout", {
                method: "POST",
                credentials: "include"
              }).then(() => {
                window.location.href = "/login"
              })
            }}
          >
            Cerrar sesión
          </button>

        </div>

        <div>
          <img
            src={profilePic}
            style={{
              height: "100px",
              width: "100px",
              borderRadius: "50px"
            }}
            alt="profile"
          />
        </div>

        <div>
          <button
            onClick={openModal}
            className="editar-perfil"
          >
            Editar perfil
          </button>
        </div>

        {/* MODAL */}
        {modalOpen && (
          <div className="modal">
            <div className="modal-contenido">

              <span className="cerrar" onClick={closeModal}>
                &times;
              </span>

              <h2>Editar perfil</h2>

              <form onSubmit={handleSubmit} encType="multipart/form-data">

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                />

                <button type="submit">
                  Guardar cambios
                </button>

              </form>

            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default Profile