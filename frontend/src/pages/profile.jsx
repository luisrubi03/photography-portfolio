import { useEffect, useState } from "react"

function Profile() {

  const [user, setUser] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(true)

  // =====================================================
  // GET USER
  // =====================================================

  useEffect(() => {

    fetch("http://localhost:5000/profile", {
      credentials: "include"
    })

      .then(res => {

        if (!res.ok) {
          throw new Error("No autenticado")
        }

        return res.json()
      })

      .then(data => {
        setUser(data)
      })

      .catch(err => {
        console.error(err)
        setUser(null)
      })

      .finally(() => {
        setLoading(false)
      })

  }, [])

//foto de perfil

  const profilePic = user?.profile_picture
    ? `http://localhost:5173/uploads/profile_pic/${user.profile_picture}`
    : `http://localhost:5173/uploads/profile_pic/default.png`



  const handleFileChange = (e) => {

    const selectedFile = e.target.files[0]

    if (!selectedFile) return

    setFile(selectedFile)
  }

//submit

  const handleSubmit = async (e) => {

    e.preventDefault()

    if (!file) {
      alert("Selecciona una imagen")
      return
    }

    const formData = new FormData()

    formData.append("imagen", file)

    try {

      const res = await fetch(
        "http://localhost:5000/profile/edit",
        {
          method: "POST",
          credentials: "include",
          body: formData
        }
      )

      const data = await res.json()

      if (!res.ok) {
        alert(data.error || "Error subiendo imagen")
        return
      }

      if (data.success) {

        // actualizar foto sin recargar página
        setUser(prev => ({
          ...prev,
          profile_picture: data.filename
        }))

        setModalOpen(false)
        setFile(null)
      }

    } catch (err) {

      console.error(err)
      alert("Error del servidor")
    }
  }

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = async () => {

    try {

      await fetch("http://localhost:5000/logout", {
        method: "POST",
        credentials: "include"
      })

      window.location.href = "/login"

    } catch (err) {

      console.error(err)
    }
  }

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return <p>Cargando perfil...</p>
  }

  if (!user) {
    return <p>No autenticado</p>
  }

  // =====================================================
  // JSX
  // =====================================================

  return (

    <div className="fila3">

      <div className="contenedor-texto-3">

        <div className="contenedor-textodeperfil">

          <h1 className="titulo-de-perfil">
            ¡Hola {user.user}!
          </h1>

        </div>

        {/* FOTO PERFIL */}

        <div className="div-fdp">

          <img
            className="fotodeperfil"
            src={profilePic}
            alt="Foto de perfil"
            style={{
              height: "100px",
              width: "100px",
              borderRadius: "50%",
              objectFit: "cover"
            }}
          />

        </div>

        {/* BOTÓN EDITAR */}

        <button
          className="btn-editarperfil"
          onClick={() => setModalOpen(true)}
        >
          Editar perfil
        </button>

        {/* BOTÓN LOGOUT */}

        <button
          onClick={handleLogout}
          className="btn-logout"
        >
          Cerrar sesión
        </button>

        {/* MODAL */}

        {modalOpen && (

          <div className="modal">

            <div className="modal-content">

              <span
                className="onclickmodalcierre"
                onClick={() => setModalOpen(false)}
              >
                X
              </span>

              <form onSubmit={handleSubmit}>

                <label className="form-label">

                  Subir imagen

                  <input
                    className="inputfile"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                  />

                </label>

                <button type="submit">
                  Guardar
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