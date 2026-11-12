import { NavLink, useLocation } from 'react-router-dom'

export default function AdminNav() {
  const { pathname } = useLocation()
  const base = pathname.startsWith('/demo/') ? '/demo/admin' : '/admin'
  return <nav className="admin-secciones" aria-label="Secciones de administración">
    <NavLink to={base} end>Usuarios</NavLink>
    <NavLink to={`${base}/productos`}>Productos</NavLink>
  </nav>
}
