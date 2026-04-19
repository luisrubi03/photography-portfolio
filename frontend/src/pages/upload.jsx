import { useState } from "react"

function Upload() {
  const [modalOpen, setModalOpen] = useState(false)
  const [file, setFile] = useState(null)
  const [descripcion, setDescripcion] = useState("")
  const [mensaje, setMensaje] = useState("")

  const abrirModal = () => setModalOpen(true)
  const cerrarModal = () => setModalOpen(false)

  const handleFile = (e) => {
    setFile(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    const formData = new FormData()
    formData.append("imagen", file)
    formData.append("descripcion", descripcion)

    try {
      const res = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        credentials: "include",
        body: formData
      })

      const data = await res.json()

      if (data.success) {
        setMensaje("Imagen subida correctamente")
        setModalOpen(false)
      } else {
        setMensaje(data.error || "Error al subir")
      }

    } catch (err) {
      console.error(err)
      setMensaje("Error de conexión con el servidor")
    }
  }

  return (
    <div>

      <div className="contenedor-archivos">
        <h1 className="titulo-contenedor-archivos">
          Crea una publicación
        </h1>

        <button onClick={abrirModal}>
          Sube tu fotografía
        </button>
      </div>

      {/* MODAL */}
      {modalOpen && (
        <div className="modal">

          <div className="modal-content">

            <span className="close" onClick={cerrarModal}>
              &times;
            </span>

            <h2>Subir imagen</h2>

            <form onSubmit={handleSubmit}>

              <input
                type="file"
                accept="image/*"
                required
                onChange={handleFile}
              />

              <input
                type="text"
                required
                placeholder="Descripción"
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
              />

              <button type="submit">
                Subir
              </button>

            </form>

          </div>

        </div>
      )}

      {/* MENSAJE */}
      {mensaje && <p>{mensaje}</p>}

    </div>
  )
}

export default Upload