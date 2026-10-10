import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav>
      <Link to="/">Inicio</Link>
      <Link to="/panel-admin">Administración</Link>
    </nav>
  )
}

export default Navbar
