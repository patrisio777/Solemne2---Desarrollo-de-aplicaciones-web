const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '')

async function solicitar(ruta, { method = 'GET', datos, signal } = {}) {
  const token = localStorage.getItem('token')
  if (!token) throw new Error('Inicia sesión con una cuenta administradora del backend para gestionar usuarios reales.')
  let respuesta
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method, signal,
      headers: { Authorization: `Token ${token}`, ...(datos ? { 'Content-Type': 'application/json' } : {}) },
      ...(datos ? { body: JSON.stringify(datos) } : {}),
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('No se pudo conectar con el backend. Comprueba que esté iniciado e intenta de nuevo.', { cause: error })
  }
  const resultado = await respuesta.json().catch(() => null)
  if (!respuesta.ok) {
    const mensaje = resultado?.message || resultado?.error || resultado?.detail
    throw new Error(respuesta.status === 401 ? 'Tu sesión no es válida o expiró. Vuelve a iniciar sesión.' :
      respuesta.status === 403 ? 'No tienes permisos para administrar usuarios.' :
        (Array.isArray(mensaje) ? mensaje.join(' ') : mensaje) || `No se pudo completar la operación (${respuesta.status}).`)
  }
  if (!resultado || resultado.status !== 'success') throw new Error('La respuesta del backend no tiene el formato esperado.')
  return resultado
}

export async function listarUsuarios(signal) {
  const resultado = await solicitar('/users/', { signal })
  if (!Array.isArray(resultado.data)) throw new Error('No se pudo interpretar la lista de usuarios del backend.')
  return resultado.data
}
export async function consultarUsuario(id) {
  const resultado = await solicitar(`/users/${encodeURIComponent(id)}/`)
  if (!resultado.usuario) throw new Error('El backend no devolvió los datos del usuario.')
  return resultado.usuario
}
export async function crearUsuario(datos) {
  const resultado = await solicitar('/users/', { method: 'POST', datos })
  if (!resultado.usuario) throw new Error('El backend no devolvió el usuario creado. Actualiza la lista antes de reintentar.')
  return resultado.usuario
}
export async function actualizarUsuario(id, datos) {
  const resultado = await solicitar(`/users/${encodeURIComponent(id)}/`, { method: 'PATCH', datos })
  if (!resultado.usuario) throw new Error('El backend no devolvió el usuario actualizado. Actualiza la lista antes de reintentar.')
  return resultado.usuario
}
