import { useEffect, useRef, useState } from 'react'
import './PanelAdmin.css'

const endpoint = '/api/admin/usuarios/'

export default function PanelAdmin() {
  const [usuarios, setUsuarios] = useState([])
  const [actual, setActual] = useState(null)
  const [token, setToken] = useState('')
  const [estado, setEstado] = useState('cargando')
  const [busqueda, setBusqueda] = useState('')
  const [rol, setRol] = useState('todos')
  const [edicion, setEdicion] = useState(null)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [guardando, setGuardando] = useState(false)
  const dialogo = useRef(null)
  const botonEdicion = useRef(null)
  const [suspension, setSuspension] = useState(null)
  const [errorSuspension, setErrorSuspension] = useState('')
  const [suspendiendo, setSuspendiendo] = useState(false)
  const dialogoSuspension = useRef(null)
  const botonSuspension = useRef(null)
  const [activando, setActivando] = useState(null)
  const [errorActivacion, setErrorActivacion] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    fetch(endpoint, { credentials: 'same-origin', signal: controller.signal })
      .then(async response => {
        if ([401, 403].includes(response.status)) {
          setEstado('sin-acceso')
          return
        }
        if (!response.ok) throw new Error('No se pudo cargar la lista de usuarios.')
        const data = await response.json()
        setUsuarios(data.usuarios)
        setActual(data.usuario_actual_id)
        setToken(data.csrf_token)
        setEstado('listo')
      })
      .catch(error => {
        if (error.name !== 'AbortError') setEstado('error')
      })
    return () => controller.abort()
  }, [])

  const normalizar = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  const visibles = usuarios.filter(usuario =>
    (rol === 'todos' || usuario.rol === rol) &&
    normalizar(`${usuario.first_name} ${usuario.last_name} ${usuario.email} ${usuario.username}`)
      .includes(normalizar(busqueda.trim())),
  )

  function abrir(usuario, boton) {
    if (usuario.id === actual) return
    botonEdicion.current = boton
    setEdicion({ ...usuario })
    setError('')
    dialogo.current.showModal()
  }

  function cerrar() {
    if (guardando) return
    dialogo.current.close()
    setEdicion(null)
    setError('')
    botonEdicion.current?.focus()
  }

  async function guardar(event) {
    event.preventDefault()
    if (!edicion || edicion.id === actual || guardando) return
    setGuardando(true)
    setError('')
    try {
      const response = await fetch(`${endpoint}${edicion.id}/`, {
        method: 'PATCH', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
        body: JSON.stringify({
          first_name: edicion.first_name.trim(),
          last_name: edicion.last_name.trim(),
          email: edicion.email.trim(),
        }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || Object.values(data).flat().join(' ') || 'No se pudieron guardar los cambios.')
      }
      setUsuarios(prev => prev.map(usuario => usuario.id === data.id ? data : usuario))
      setMensaje(`Se actualizaron los datos de ${data.first_name} ${data.last_name}.`)
      dialogo.current.close()
      setEdicion(null)
      botonEdicion.current?.focus()
    } catch (error) {
      setError(error instanceof SyntaxError ? 'El servidor no respondió correctamente. Intenta nuevamente.' : error.message)
    } finally {
      setGuardando(false)
    }
  }

  function abrirSuspension(usuario, boton) {
    if (usuario.id === actual || !usuario.is_active) return
    botonSuspension.current = boton
    setSuspension(usuario)
    setErrorSuspension('')
    dialogoSuspension.current.showModal()
  }

  function cerrarSuspension() {
    if (suspendiendo) return
    dialogoSuspension.current.close()
    setSuspension(null)
    setErrorSuspension('')
    botonSuspension.current?.focus()
  }

  async function suspender(event) {
    event.preventDefault()
    if (!suspension || suspension.id === actual || suspendiendo) return
    setSuspendiendo(true)
    setErrorSuspension('')
    try {
      const response = await fetch(`${endpoint}${suspension.id}/suspender/`, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'X-CSRFToken': token },
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'No se pudo suspender la cuenta. Intenta nuevamente.')
      setUsuarios(prev => prev.map(usuario => usuario.id === data.id ? data : usuario))
      setMensaje(`La cuenta de ${`${data.first_name} ${data.last_name}`.trim() || data.username} fue suspendida.`)
      dialogoSuspension.current.close()
      setSuspension(null)
      botonSuspension.current?.focus()
    } catch (error) {
      setErrorSuspension(error instanceof SyntaxError ? 'El servidor no respondió correctamente. Intenta nuevamente.' : error.message)
    } finally {
      setSuspendiendo(false)
    }
  }

  async function activar(usuario) {
    if (usuario.id === actual || usuario.is_active || activando !== null) return
    setActivando(usuario.id)
    setErrorActivacion('')
    try {
      const response = await fetch(`${endpoint}${usuario.id}/activar/`, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'X-CSRFToken': token },
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'No se pudo activar la cuenta. Intenta nuevamente.')
      setUsuarios(prev => prev.map(item => item.id === data.id ? data : item))
      setMensaje(`La cuenta de ${`${data.first_name} ${data.last_name}`.trim() || data.username} fue activada.`)
    } catch (error) {
      setErrorActivacion(error instanceof SyntaxError ? 'El servidor no respondió correctamente. Intenta nuevamente.' : error.message)
    } finally {
      setActivando(null)
    }
  }

  return (
    <section className="panel-admin" aria-labelledby="panel-titulo">
      <header className="panel-cabecera">
        <div><p className="panel-etiqueta">Administración / Usuarios</p>
          <h1 id="panel-titulo">Panel de control</h1>
          <p>Gestiona los datos de tus clientes y administradores.</p>
        </div>
        <span className="panel-sello">Cafetería · Gestión de cuentas</span>
      </header>

      {estado === 'cargando' && <p role="status" className="panel-aviso">Cargando usuarios…</p>}
      {estado === 'sin-acceso' && <div className="panel-aviso" role="status">
        <h2>Acceso de administrador</h2>
        <p>Inicia sesión con una cuenta de administrador para gestionar usuarios.</p>
        <a href="/admin/login/?next=/panel-admin">Iniciar sesión de administrador</a>
      </div>}
      {estado === 'error' && <div className="panel-aviso" role="alert">
        <p>No se pudo cargar la lista. Comprueba la conexión con el servidor.</p>
        <button onClick={() => window.location.reload()}>Reintentar</button>
      </div>}

      {estado === 'listo' && <>
        <div className="panel-resumen" aria-label="Resumen de usuarios">
          <div><span>Total de usuarios</span><strong>{usuarios.length}</strong></div>
          <div><span>Clientes</span><strong>{usuarios.filter(u => u.rol === 'cliente').length}</strong></div>
          <div><span>Administradores</span><strong>{usuarios.filter(u => u.rol === 'admin').length}</strong></div>
        </div>
        <div className="panel-filtros">
          <label>Buscar usuario<input type="search" value={busqueda} onChange={e => setBusqueda(e.target.value)} placeholder="Nombre, correo o usuario" /></label>
          <label>Tipo de cuenta<select value={rol} onChange={e => setRol(e.target.value)}>
            <option value="todos">Todas las cuentas</option><option value="cliente">Clientes</option><option value="admin">Administradores</option>
          </select></label>
        </div>
        <p className="panel-nota">Tu cuenta aparece en la lista, pero no puede editarse ni suspenderse desde este panel.</p>
        <p className="panel-mensaje" role="status">{mensaje}</p>
        {errorActivacion && <p className="panel-error" role="alert">{errorActivacion}</p>}
        <div className="panel-tabla">
          <table>
            <caption>{visibles.length} {visibles.length === 1 ? 'usuario encontrado' : 'usuarios encontrados'}</caption>
            <thead><tr><th scope="col">Usuario</th><th scope="col">Correo electrónico</th><th scope="col">Tipo de cuenta</th><th scope="col">Estado</th><th scope="col">Acciones</th></tr></thead>
            <tbody>{visibles.map(usuario => <tr key={usuario.id}>
              <td><strong>{`${usuario.first_name} ${usuario.last_name}`.trim() || usuario.username}</strong><small>@{usuario.username}{usuario.id === actual && ' · Tu cuenta'}</small></td>
              <td>{usuario.email || 'Sin correo registrado'}</td>
              <td><span className={`panel-rol ${usuario.rol}`}>{usuario.rol === 'admin' ? 'Administrador' : 'Cliente'}</span></td>
              <td><span className={`panel-estado ${usuario.is_active ? 'activa' : 'suspendida'}`}>{usuario.is_active ? 'Activa' : 'Suspendida'}</span></td>
              <td><div className="panel-acciones-fila"><button disabled={usuario.id === actual} onClick={e => abrir(usuario, e.currentTarget)} aria-label={`Editar datos de ${usuario.username}`}>
                {usuario.id === actual ? 'Tu cuenta' : 'Editar datos'}
              </button><button className={usuario.is_active ? 'panel-boton-suspender' : 'panel-boton-activar'} disabled={usuario.id === actual || activando !== null} onClick={e => usuario.is_active ? abrirSuspension(usuario, e.currentTarget) : activar(usuario)} aria-label={`${usuario.is_active ? 'Suspender' : 'Activar'} cuenta de ${usuario.username}`}>
                {activando === usuario.id ? 'Activando…' : usuario.is_active ? 'Suspender' : 'Activar cuenta'}
              </button></div></td>
            </tr>)}</tbody>
          </table>
          {visibles.length === 0 && <p className="panel-vacio">{usuarios.length === 0 ? 'Todavía no hay usuarios registrados.' : 'No hay usuarios que coincidan con tu búsqueda.'}</p>}
        </div>
      </>}

      <dialog ref={dialogo} className="panel-dialogo" aria-labelledby="editar-titulo" onCancel={e => { e.preventDefault(); cerrar() }}>
        {edicion && <form onSubmit={guardar}>
          <p className="panel-etiqueta">Datos de usuario</p><h2 id="editar-titulo">Editar cuenta</h2>
          <p className="panel-nota">@{edicion.username} · {edicion.rol === 'admin' ? 'Administrador' : 'Cliente'}</p>
          <fieldset disabled={guardando}>
            <label>Nombre<input autoFocus required maxLength={150} value={edicion.first_name} onChange={e => setEdicion({ ...edicion, first_name: e.target.value })} /></label>
            <label>Apellido<input required maxLength={150} value={edicion.last_name} onChange={e => setEdicion({ ...edicion, last_name: e.target.value })} /></label>
            <label>Correo electrónico<input type="email" required maxLength={254} value={edicion.email} onChange={e => setEdicion({ ...edicion, email: e.target.value })} /></label>
          </fieldset>
          {error && <p className="panel-error" role="alert">{error}</p>}
          <div className="panel-acciones"><button type="button" disabled={guardando} onClick={cerrar}>Cancelar</button><button type="submit" disabled={guardando}>{guardando ? 'Guardando…' : 'Guardar cambios'}</button></div>
        </form>}
      </dialog>

      <dialog ref={dialogoSuspension} className="panel-dialogo" aria-labelledby="suspender-titulo" aria-describedby="suspender-descripcion" onCancel={e => { e.preventDefault(); cerrarSuspension() }}>
        {suspension && <form onSubmit={suspender}>
          <p className="panel-etiqueta">Confirmación de suspensión</p>
          <h2 id="suspender-titulo">¿Suspender esta cuenta?</h2>
          <p className="panel-cuenta-confirmacion"><strong>{`${suspension.first_name} ${suspension.last_name}`.trim() || suspension.username}</strong><br />{suspension.email}<br />{suspension.rol === 'admin' ? 'Administrador' : 'Cliente'}</p>
          <p id="suspender-descripcion">Esta persona perderá el acceso a su cuenta{ suspension.rol === 'admin' ? ' y al panel de administración' : '' }. Sus datos se conservarán.</p>
          {errorSuspension && <p className="panel-error" role="alert">{errorSuspension}</p>}
          <div className="panel-acciones"><button autoFocus type="button" disabled={suspendiendo} onClick={cerrarSuspension}>Cancelar</button><button type="submit" className="panel-confirmar-suspension" disabled={suspendiendo}>{suspendiendo ? 'Suspendiendo…' : 'Confirmar suspensión'}</button></div>
        </form>}
      </dialog>
    </section>
  )
}
