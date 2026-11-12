import { useEffect, useRef, useState } from 'react'
import '../wireframe.css'
import './Admin.css'
import AdminNav from '../components/AdminNav'
import { listarUsuarios, consultarUsuario, crearUsuario, actualizarUsuario } from '../services/usuarios'

function normalizar(usuario, cuenta) {
  return { id: usuario.id, nombre: usuario.first_name || '', apellido: usuario.last_name || '', email: usuario.email,
    admin: usuario.es_admin, activo: usuario.is_active,
    propia: String(usuario.email).toLowerCase() === String(cuenta.email).toLowerCase(), fecha: usuario.fecha_registro }
}

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
  const [cuenta] = useState(() => JSON.parse(localStorage.getItem('usuario') || '{}'))
  const demostracion = demo || cuenta.demo === true
  const [usuarios, setUsuarios] = useState(() => demostracion ? iniciales(demo) : [])
  const [seleccion, setSeleccion] = useState(null)
  const [datos, setDatos] = useState({ nombre: '', apellido: '', email: '', password: '', confirmar: '' })
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const [errorServidor, setErrorServidor] = useState('')
  const [cargando, setCargando] = useState(!demostracion)
  const [guardando, setGuardando] = useState(false)
  const [revision, setRevision] = useState(0)
  const [modalAbierto, setModalAbierto] = useState(false)
  const pendiente = useRef(false)
  const dialogo = useRef(null)
  const origen = useRef(null)
  const editando = seleccion?.accion === 'editar'
  const creando = seleccion?.accion === 'crear'
  const consultando = seleccion?.accion === 'consultar'
  const formulario = editando || creando
  const bloquear = seleccion?.usuario?.activo
  const accion = bloquear ? 'Bloquear' : 'Reactivar'

  useEffect(() => {
    if (demostracion) return
    const controller = new AbortController()
    listarUsuarios(controller.signal).then(lista => {
      setUsuarios(lista.map(usuario => normalizar(usuario, cuenta)))
      setErrorServidor('')
    }).catch(error => {
      if (error.name !== 'AbortError') setErrorServidor(error.message)
    }).finally(() => {
      if (!controller.signal.aborted) setCargando(false)
    })
    return () => controller.abort()
  }, [demostracion, cuenta, revision])

  async function abrir(usuario, tipo, evento) {
    if (pendiente.current || (usuario?.propia && tipo !== 'consultar')) return
    origen.current = evento.currentTarget
    setSeleccion({ usuario, accion: tipo })
    setDatos({ nombre: usuario?.nombre || '', apellido: usuario?.apellido || '', email: usuario?.email || '', password: '', confirmar: '' })
    setErrores({})
    setMensaje('')
    setErrorServidor('')
    setModalAbierto(true)
    dialogo.current.showModal()
    if (!demostracion && tipo === 'consultar') {
      pendiente.current = true
      setGuardando(true)
      try {
        const resultado = await consultarUsuario(usuario.id)
        setSeleccion({ usuario: normalizar(resultado, cuenta), accion: tipo })
      } catch (error) { setErrorServidor(error.message) }
      finally { pendiente.current = false; setGuardando(false) }
    }
  }

  async function guardar(evento) {
    evento.preventDefault()
    if (!seleccion || consultando || pendiente.current || seleccion.usuario?.propia) return
    const usuario = seleccion.usuario
    const limpios = { nombre: datos.nombre.trim(), apellido: datos.apellido.trim(), email: datos.email.trim().toLowerCase() }
    if (formulario) {
      const nuevos = {}
      if (!limpios.nombre) nuevos.nombre = 'Ingresa un nombre.'
      if (!limpios.apellido) nuevos.apellido = 'Ingresa un apellido.'
      if (!limpios.email) nuevos.email = 'Ingresa un correo.'
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(limpios.email)) nuevos.email = 'Ingresa un correo válido.'
      if (limpios.nombre.length > 150) nuevos.nombre = 'El nombre no puede superar 150 caracteres.'
      if (limpios.apellido.length > 150) nuevos.apellido = 'El apellido no puede superar 150 caracteres.'
      if (limpios.email.length > 150) nuevos.email = 'El correo no puede superar 150 caracteres.'
      if (creando && datos.password.length < 8) nuevos.password = 'La contraseña debe tener al menos 8 caracteres.'
      if (creando && datos.confirmar !== datos.password) nuevos.confirmar = 'Las contraseñas no coinciden.'
      if (demostracion && usuarios.some(item => item.id !== usuario?.id && item.email.toLowerCase() === limpios.email)) nuevos.email = 'Este correo ya está registrado.'
      setErrores(nuevos)
      if (Object.keys(nuevos).length) {
        dialogo.current.querySelector(`[name="${Object.keys(nuevos)[0]}"]`)?.focus()
        return
      }
    }
    pendiente.current = true
    setGuardando(true)
    setErrorServidor('')
    try {
      let actualizado
      if (demostracion) {
        actualizado = creando ? { ...limpios, id: crypto.randomUUID(), admin: false, activo: true, propia: false } :
          editando ? { ...usuario, ...limpios } : { ...usuario, activo: !usuario.activo }
      } else {
        const payload = formulario ? { first_name: limpios.nombre, last_name: limpios.apellido, email: limpios.email,
          ...(creando ? { password: datos.password, es_admin: false } : {}) } : { is_active: !usuario.activo }
        const resultado = creando ? await crearUsuario(payload) : await actualizarUsuario(usuario.id, payload)
        actualizado = normalizar(resultado, cuenta)
      }
      setUsuarios(actuales => creando ? [...actuales, actualizado] : actuales.map(item => item.id === usuario.id ? actualizado : item))
      setMensaje(`${actualizado.nombre} ${actualizado.apellido}: ${creando ? 'usuario creado' : editando ? 'datos actualizados' : actualizado.activo ? 'cuenta reactivada' : 'cuenta bloqueada'}${demostracion ? ' en la demostración' : ''}.`)
      setDatos({ nombre: '', apellido: '', email: '', password: '', confirmar: '' })
      dialogo.current.close()
    } catch (error) { setErrorServidor(error.message) }
    finally { pendiente.current = false; setGuardando(false) }
  }

  return (
    <section className="store admin-panel" data-theme={tema} aria-labelledby="admin-titulo">
      <AdminNav />
      <header className="admin-cabecera">
        <p className="admin-etiqueta">Paraíso del Café / Administración</p>
        <h1 id="admin-titulo">Gestión de usuarios</h1>
        <p>Administra los datos y el acceso de quienes forman parte de nuestro café.</p>
      </header>
      <div className="admin-demo">{demostracion ? <><strong>Modo demostración.</strong> Datos de ejemplo: los cambios se restablecen al recargar. Para gestionar cuentas reales, inicia sesión con el correo y la contraseña de un administrador del backend.</> : <><strong>Administración conectada.</strong> Los cambios se guardan en las cuentas del sistema.</>}</div>
      <div role="status" aria-live="polite">{mensaje && <p className="alert alert-success">{mensaje}</p>}</div>
      {errorServidor && !modalAbierto && <p className="alert alert-danger" role="alert">{errorServidor}</p>}
      <div className="admin-lista">
        <div className="admin-lista-titulo"><h2>Usuarios</h2><span>{usuarios.length} cuentas · {usuarios.filter(usuario => usuario.activo).length} activas</span><div className="admin-acciones">{!demostracion && <button className="btn" disabled={cargando || guardando} onClick={() => { setCargando(true); setRevision(actual => actual + 1) }}>Actualizar lista</button>}<button className="btn admin-guardar" disabled={cargando || guardando || (!demostracion && !!errorServidor)} onClick={evento => abrir(null, 'crear', evento)}>Crear usuario</button></div></div>
        {cargando && <p role="status">Cargando usuarios…</p>}
        {!cargando && !usuarios.length && !errorServidor && <p>No hay usuarios registrados.</p>}
        <div className="table-responsive" role="region" aria-label="Tabla de usuarios, desplazable horizontalmente" tabIndex={0}>
          <table className="table align-middle mb-0">
            <caption className="visually-hidden">Clientes y administradores. Tu cuenta no se puede modificar desde este panel.</caption>
            <thead><tr>{['Nombre', 'Apellido', 'Correo', 'Rol', 'Estado', 'Acciones'].map(titulo => <th scope="col" key={titulo}>{titulo}</th>)}</tr></thead>
            <tbody>{usuarios.map(usuario => <tr key={usuario.id}>
              <th scope="row">{usuario.nombre}{usuario.propia && <small className="admin-propia">Tu cuenta</small>}</th>
              <td>{usuario.apellido}</td><td>{usuario.email}</td><td>{usuario.admin ? 'Administrador' : 'Cliente'}</td>
              <td><span className={`admin-estado ${usuario.activo ? 'activo' : 'suspendido'}`}>{usuario.activo ? 'Activa' : 'Suspendida'}</span></td>
              <td><div className="admin-acciones">
                <button className="btn btn-sm" disabled={cargando || guardando} aria-label={`Consultar a ${usuario.nombre} ${usuario.apellido}`} onClick={evento => abrir(usuario, 'consultar', evento)}>Consultar</button>
                <button className="btn btn-sm admin-editar" disabled={usuario.propia || cargando || guardando} aria-label={`Editar a ${usuario.nombre} ${usuario.apellido}`} onClick={evento => abrir(usuario, 'editar', evento)}>Editar</button>
                <button className={`btn btn-sm ${usuario.activo ? 'btn-outline-danger' : 'btn-outline-success'}`} disabled={usuario.propia || cargando || guardando} aria-label={`${usuario.activo ? 'Bloquear' : 'Reactivar'} a ${usuario.nombre} ${usuario.apellido}`} onClick={evento => abrir(usuario, 'estado', evento)}>{usuario.activo ? 'Bloquear' : 'Reactivar'}</button>
              </div></td>
            </tr>)}</tbody>
          </table>
        </div>
        <p className="admin-nota">Tu cuenta no se puede editar, bloquear ni reactivar desde esta tabla.</p>
      </div>
      <dialog ref={dialogo} className="admin-dialogo" aria-labelledby="dialogo-titulo" aria-describedby={formulario || consultando ? undefined : 'dialogo-descripcion'} onCancel={evento => { if (pendiente.current) evento.preventDefault() }} onClose={() => { setModalAbierto(false); setDatos(actual => ({ ...actual, password: '', confirmar: '' })); origen.current?.focus() }}>
        <form onSubmit={guardar} noValidate>
          <p className="admin-etiqueta">{formulario || consultando ? 'Datos de la cuenta' : 'Confirmar cambio de acceso'}</p>
          <h2 id="dialogo-titulo">{creando ? 'Crear usuario' : consultando ? 'Consultar usuario' : editando ? 'Editar usuario' : `${accion} cuenta`}</h2>
          {errorServidor && <p className="alert alert-danger" role="alert">{errorServidor}</p>}
          {formulario ? <div className="admin-campos">{[['nombre', 'Nombre'], ['apellido', 'Apellido'], ['email', 'Correo'], ...(creando ? [['password', 'Contraseña'], ['confirmar', 'Confirmar contraseña']] : [])].map(([campo, etiqueta]) => <div key={campo}>
            <label className="form-label" htmlFor={`admin-${campo}`}>{etiqueta}</label>
            <input id={`admin-${campo}`} name={campo} type={campo === 'email' ? 'email' : ['password', 'confirmar'].includes(campo) ? 'password' : 'text'} autoComplete={['password', 'confirmar'].includes(campo) ? 'new-password' : undefined} disabled={guardando} className={`form-control ${errores[campo] ? 'is-invalid' : ''}`} value={datos[campo]} required aria-invalid={!!errores[campo]} aria-describedby={errores[campo] ? `error-${campo}` : undefined} onChange={evento => setDatos({ ...datos, [campo]: evento.target.value })} />
            {errores[campo] && <div id={`error-${campo}`} className="invalid-feedback">{errores[campo]}</div>}
          </div>)}{creando && <p className="admin-nota">La cuenta se creará como cliente. Usa una contraseña de al menos 8 caracteres que no sea común, completamente numérica ni similar a los datos de la persona.</p>}</div> : consultando ? (guardando ? <p role="status">Consultando usuario…</p> : <dl className="admin-detalle"><dt>Nombre</dt><dd>{seleccion?.usuario.nombre} {seleccion?.usuario.apellido}</dd><dt>Correo</dt><dd>{seleccion?.usuario.email}</dd><dt>Rol</dt><dd>{seleccion?.usuario.admin ? 'Administrador' : 'Cliente'}</dd><dt>Estado</dt><dd>{seleccion?.usuario.activo ? 'Activa' : 'Suspendida'}</dd>{seleccion?.usuario.fecha && <><dt>Fecha de registro</dt><dd>{seleccion.usuario.fecha}</dd></>}</dl>) : <p id="dialogo-descripcion">¿Quieres {bloquear ? 'bloquear' : 'reactivar'} la cuenta de <strong>{seleccion?.usuario.nombre} {seleccion?.usuario.apellido}</strong>? {bloquear ? 'Su estado pasará a suspendida.' : 'Su estado volverá a activa.'} {demostracion ? 'Este cambio solo afecta la demostración.' : 'Se actualizará su acceso al sistema.'}</p>}
          <div className="admin-dialogo-acciones">
            <button type="button" disabled={guardando} className="btn btn-outline-secondary" onClick={() => dialogo.current.close()}>{consultando ? 'Cerrar' : 'Cancelar'}</button>
            {!consultando && <button type="submit" disabled={guardando} className={`btn ${formulario ? 'admin-guardar' : bloquear ? 'btn-danger' : 'btn-success'}`}>{guardando ? 'Guardando…' : creando ? 'Crear usuario' : editando ? 'Guardar cambios' : `${accion} cuenta`}</button>}
          </div>
        </form>
      </dialog>
    </section>
  )
}

export default Admin
