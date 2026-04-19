import { Outlet, useLocation } from "react-router-dom"
import { useEffect, useState } from "react"
import Navbar from "../components/Navbar.jsx"

function Layout() {
  const location = useLocation()
  const [user, setUser] = useState(null)

  const hideNavbarRoutes = ["/login", "/register"]
  const showNavbar = !hideNavbarRoutes.includes(location.pathname)

  useEffect(() => {
    fetch("http://localhost:5000/api/user", {
      credentials: "include"
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => setUser(data))
      .catch(() => setUser(null))
  }, [])

  return (
    <>
      {showNavbar && <Navbar user={user} />}

      <main>
        <Outlet />
      </main>
    </>
  )
}

export default Layout