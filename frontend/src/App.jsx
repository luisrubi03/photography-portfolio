import { useEffect, useState } from "react"
import "./App.scss"
import { Routes, Route } from "react-router-dom"

import Home from "./pages/Home"
import Login from "./pages/Login"
import ProtectedRoute from "./components/ProtectedRoute"
import Layout from "./pages/Layout.jsx"
import Profile from "./pages/profile.jsx";
import Upload from "./pages/Upload.jsx"

function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetch("http://localhost:5000/api/user", {
      credentials: "include"
    })
      .then(res => {
        if (!res.ok) throw new Error()
        return res.json()
      })
      .then(data => setUser(data))
      .catch(() => setUser(null))
  }, [])

  return (
    <main>
        <div
          className="bg-blur"
          style={{
            backgroundImage: "url('/assets/background1.jpg')"
          }}
        />

        <div className="app-content">
            {/* app */}
        </div>
      <Routes>
           <Route element={<Layout />}>
                <Route path="/" element={<Home />}
                />
               <Route path="/profile" element={<Profile />} />
               <Route path="/upload" element={<Upload />} />
           </Route>
        <Route path="/login" element={<Login />} />
      </Routes>
    </main>
  )
}

export default App