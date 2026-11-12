import { Navigate } from 'react-router-dom'

// solo deja pasar a los administradores
function RutaAdmin({ children }) {
  const usuario = JSON.parse(localStorage.getItem('usuario'))
  if (!usuario || !usuario.es_admin) {
    return <Navigate to="/" replace />
  }
  return children
}

export default RutaAdmin