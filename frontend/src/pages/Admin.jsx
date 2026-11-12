import { useRef, useState } from 'react'
import '../wireframe.css'
import './Admin.css'
import AdminNav from '../components/AdminNav'

function iniciales(demo) {
  const cuenta = demo ? {} : JSON.parse(localStorage.getItem('usuario') || '{}')
  return [
    { id: 'yo', nombre: cuenta.nombre || 'Admin1', apellido: cuenta.apellido || 'Demo', email: cuenta.email || 'admin1@ejemplo.cl', admin: true, activo: true, propia: true },
    { id: 'jose', nombre: 'José', apellido: 'Argüello', email: 'jose@ejemplo.cl', admin: false, activo: true },
    { id: 'patricio', nombre: 'Patricio', apellido: 'Chaug', email: 'patricio@ejemplo.cl', admin: false, activo: false },
    { id: 'javiera', nombre: 'Javiera', apellido: 'Fuentealba', email: 'javiera@ejemplo.cl', admin: false, activo: true },
    { id: 'brandon', nombre: 'Brandon', apellido: 'Valdés', email: 'brandon@ejemplo.cl', admin: false, activo: true },
    { id: 'gabriel', nombre: 'Gabriel', apellido: 'Moreno', email: 'gabriel@ejemplo.cl', admin: false, activo: true },
    { id: 'cristobal', nombre: 'Cristóbal', apellido: 'Garrido', email: 'cristobal@ejemplo.cl', admin: false, activo: true },
  ]
}

function Admin({ demo = false, tema = 'claro' }) {
  const [usuarios, setUsuarios] = useState(() => iniciales(demo))
  const [seleccion, setSeleccion] = useState(null)
  const [datos, setDatos] = useState({ nombre: '', apellido: '', email: '' })
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const dialogo = useRef(null)
  const origen = useRef(null)
  const editando = seleccion?.accion === 'editar'
  const bloquear = seleccion?.usuario.activo
  const accion = bloquear ? 'Bloquear' : 'Reactivar'

  function abrir(usuario, tipo, evento) {
    if (usuario.propia) return
    origen.current = evento.currentTarget
    setSeleccion({ usuario, accion: tipo })
    setDatos({ nombre: usuario.nombre, apellido: usuario.apellido, email: usuario.email })
    setErrores({})
    setMensaje('')
    dialogo.current.showModal()
  }

  function guardar(evento) {
    evento.preventDefault()
    if (!seleccion || seleccion.usuario.propia) return
    const usuario = seleccion.usuario
    if (editando) {
      const limpios = Object.fromEntries(Object.entries(datos).map(([campo, valor]) => [campo, valor.trim()]))
      const nuevos = {}
      if (!limpios.nombre) nuevos.nombre = 'Ingresa un nombre.'
      if (!limpios.apellido) nuevos.apellido = 'Ingresa un apellido.'
      if (!limpios.email) nuevos.email = 'Ingresa un correo.'
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(limpios.email)) nuevos.email = 'Ingresa un correo válido.'
      setErrores(nuevos)
      if (Object.keys(nuevos).length) {
        dialogo.current.querySelector(`[name="${Object.keys(nuevos)[0]}"]`)?.focus()
        return
      }
      setUsuarios(actuales => actuales.map(item => item.id === usuario.id ? { ...item, ...limpios } : item))
      setMensaje(`Los datos de ${limpios.nombre} ${limpios.apellido} se actualizaron en la demostración.`)
    } else {
      setUsuarios(actuales => actuales.map(item => item.id === usuario.id ? { ...item, activo: !item.activo } : item))
      setMensaje(`La cuenta de ${usuario.nombre} ${usuario.apellido} fue ${usuario.activo ? 'bloqueada' : 'reactivada'} en la demostración.`)
    }
    dialogo.current.close()
  }

  return (
    <section className="store admin-panel" data-theme={tema} aria-labelledby="admin-titulo">
      <AdminNav />
      <header className="admin-cabecera">
        <p className="admin-etiqueta">Paraíso del Café / Administración</p>
        <h1 id="admin-titulo">Gestión de usuarios</h1>
        <p>Administra los datos y el acceso de quienes forman parte de nuestro café.</p>
      </header>
      <div className="admin-demo"><strong>Modo demostración.</strong> Datos de ejemplo: los cambios solo se reflejan en esta pantalla y se restablecen al recargar.</div>
      <div role="status" aria-live="polite">{mensaje && <p className="alert alert-success">{mensaje}</p>}</div>
      <div className="admin-lista">
        <div className="admin-lista-titulo"><h2>Usuarios</h2><span>{usuarios.length} cuentas · {usuarios.filter(usuario => usuario.activo).length} activas</span></div>
        <div className="table-responsive" role="region" aria-label="Tabla de usuarios, desplazable horizontalmente" tabIndex={0}>
          <table className="table align-middle mb-0">
            <caption className="visually-hidden">Clientes y administradores. Tu cuenta no se puede modificar desde este panel.</caption>
            <thead><tr>{['Nombre', 'Apellido', 'Correo', 'Rol', 'Estado', 'Acciones'].map(titulo => <th scope="col" key={titulo}>{titulo}</th>)}</tr></thead>
            <tbody>{usuarios.map(usuario => <tr key={usuario.id}>
              <th scope="row">{usuario.nombre}{usuario.propia && <small className="admin-propia">Tu cuenta</small>}</th>
              <td>{usuario.apellido}</td><td>{usuario.email}</td><td>{usuario.admin ? 'Administrador' : 'Cliente'}</td>
              <td><span className={`admin-estado ${usuario.activo ? 'activo' : 'suspendido'}`}>{usuario.activo ? 'Activa' : 'Suspendida'}</span></td>
              <td><div className="admin-acciones">
                <button className="btn btn-sm admin-editar" disabled={usuario.propia} aria-label={`Editar a ${usuario.nombre} ${usuario.apellido}`} onClick={evento => abrir(usuario, 'editar', evento)}>Editar</button>
                <button className={`btn btn-sm ${usuario.activo ? 'btn-outline-danger' : 'btn-outline-success'}`} disabled={usuario.propia} aria-label={`${usuario.activo ? 'Bloquear' : 'Reactivar'} a ${usuario.nombre} ${usuario.apellido}`} onClick={evento => abrir(usuario, 'estado', evento)}>{usuario.activo ? 'Bloquear' : 'Reactivar'}</button>
              </div></td>
            </tr>)}</tbody>
          </table>
        </div>
        <p className="admin-nota">Tu cuenta no se puede editar, bloquear ni reactivar desde esta tabla.</p>
      </div>
      <dialog ref={dialogo} className="admin-dialogo" aria-labelledby="dialogo-titulo" aria-describedby={editando ? undefined : 'dialogo-descripcion'} onClose={() => origen.current?.focus()}>
        <form onSubmit={guardar} noValidate>
          <p className="admin-etiqueta">{editando ? 'Datos de la cuenta' : 'Confirmar cambio de acceso'}</p>
          <h2 id="dialogo-titulo">{editando ? 'Editar usuario' : `${accion} cuenta`}</h2>
          {editando ? <div className="admin-campos">{[['nombre', 'Nombre'], ['apellido', 'Apellido'], ['email', 'Correo']].map(([campo, etiqueta]) => <div key={campo}>
            <label className="form-label" htmlFor={`admin-${campo}`}>{etiqueta}</label>
            <input id={`admin-${campo}`} name={campo} type={campo === 'email' ? 'email' : 'text'} className={`form-control ${errores[campo] ? 'is-invalid' : ''}`} value={datos[campo]} required aria-invalid={!!errores[campo]} aria-describedby={errores[campo] ? `error-${campo}` : undefined} onChange={evento => setDatos({ ...datos, [campo]: evento.target.value })} />
            {errores[campo] && <div id={`error-${campo}`} className="invalid-feedback">{errores[campo]}</div>}
          </div>)}</div> : <p id="dialogo-descripcion">¿Quieres {bloquear ? 'bloquear' : 'reactivar'} la cuenta de <strong>{seleccion?.usuario.nombre} {seleccion?.usuario.apellido}</strong>? {bloquear ? 'Su estado pasará a suspendida.' : 'Su estado volverá a activa.'} Este cambio solo afecta la demostración.</p>}
          <div className="admin-dialogo-acciones">
            <button type="button" className="btn btn-outline-secondary" onClick={() => dialogo.current.close()}>Cancelar</button>
            <button type="submit" className={`btn ${editando ? 'admin-guardar' : bloquear ? 'btn-danger' : 'btn-success'}`}>{editando ? 'Guardar cambios' : `${accion} cuenta`}</button>
          </div>
        </form>
      </dialog>
    </section>
  )
}

export default Admin
