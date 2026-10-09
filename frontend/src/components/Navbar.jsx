import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav>
      <Link to="/">Inicio</Link>
      <Link to="/catalogo">Catálogo</Link>
      <Link to="/quienes-somos">Quiénes somos</Link>
      <Link to="/contacto">Contacto</Link>
      <Link to="/carrito">Carrito</Link>
      <Link to="/login">Iniciar sesión</Link>
    </nav>
  )
}

export default Navbar