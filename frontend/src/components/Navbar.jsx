import { Link, useNavigate, useLocation } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function Navbar({ tema, onTemaChange }) {
  const navigate = useNavigate()
  // hace que el menú se actualice al cambiar de página (por ejemplo, después del login)
  useLocation()
  const usuario = JSON.parse(localStorage.getItem('usuario'))

  async function cerrarSesion() {
    const token = localStorage.getItem('token')
    try {
      if (token && !usuario?.demo) await fetch(`${API_URL}/logout/`, {
        method: 'POST',
        headers: { Authorization: `Token ${token}` }
      })
    } catch {
      // si el servidor no responde, igual se borra la sesión del navegador
    }
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
    navigate('/')
  }

  return (
    <nav className="site-nav" aria-label="Navegación principal">
      <Link to="/">Inicio</Link>
      <Link to="/catalogo">Catálogo</Link>
      <Link to="/quienes-somos">Quiénes somos</Link>
      <Link to="/contacto">Contacto</Link>
      {!usuario?.es_admin && <Link to="/carrito">Carrito</Link>}
      {usuario?.es_admin && <Link to="/admin">Panel</Link>}
      {usuario ? (
        <>
          <span>Hola, {usuario.nombre}</span>
          <button type="button" onClick={cerrarSesion}>Cerrar sesión</button>
        </>
      ) : (
        <Link to="/login">Iniciar sesión</Link>
      )}
      <div className="site-theme">
        <label htmlFor="site-tema">Apariencia</label>
        <select id="site-tema" value={tema} onChange={evento => onTemaChange(evento.target.value)}>
          <option value="claro">Claro</option>
          <option value="oscuro">Oscuro</option>
          <option value="vintage">Vintage</option>
          <option value="pastel">Pastel</option>
        </select>
      </div>
    </nav>
  )
}

export default Navbar
