import { useRef, useState } from 'react'
import AdminNav from '../components/AdminNav'
import capuccino from '../assets/capuccino.jpg'
import mocha from '../assets/mocha.jpg'
import './Admin.css'
import './AdminProductos.css'

const vacio = { nombre: '', descripcion: '', categoria: '', precio: '', stock: '', imagen: '' }
const categorias = ['Café', 'Repostería', 'Accesorios']
const iniciales = [
  { id: 'capuccino', nombre: 'Capuccino', descripcion: 'Espresso con leche y una suave capa de espuma.', categoria: 'Café', precio: 3800, stock: 20, imagen: capuccino },
  { id: 'mocha', nombre: 'Mocha', descripcion: 'Café con chocolate y leche.', categoria: 'Café', precio: 4200, stock: 0, imagen: mocha },
]
const pesos = new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' })

export default function AdminProductos() {
  const [productos, setProductos] = useState(iniciales)
  const [datos, setDatos] = useState(vacio)
  const [editando, setEditando] = useState(null)
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const [leyendo, setLeyendo] = useState(false)
  const formulario = useRef(null)
  const archivo = useRef(null)
  const lectura = useRef(0)

  function limpiar() {
    lectura.current += 1
    setLeyendo(false)
    setDatos(vacio)
    setEditando(null)
    setErrores({})
    if (archivo.current) archivo.current.value = ''
  }

  function editar(producto) {
    limpiar()
    setDatos({ ...producto })
    setEditando(producto.id)
    setMensaje('')
    formulario.current.querySelector('[name="nombre"]').focus()
    formulario.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  async function cargarImagen(evento) {
    const fichero = evento.target.files?.[0]
    if (!fichero) return
    const version = ++lectura.current
    setLeyendo(true)
    let error = ''
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(fichero.type)) error = 'Selecciona una imagen JPG, PNG o WebP.'
    else if (fichero.size > 5 * 1024 * 1024) error = 'La imagen no puede superar los 5 MB.'
    else {
      try {
        const contenido = await new Promise((resolve, reject) => {
          const lector = new FileReader()
          lector.onload = () => resolve(lector.result)
          lector.onerror = reject
          lector.readAsDataURL(fichero)
        })
        const imagen = new Image()
        imagen.src = contenido
        await imagen.decode()
        if (version !== lectura.current) return
        setDatos(actual => ({ ...actual, imagen: contenido }))
      } catch { error = 'No se pudo leer la imagen. Prueba con otro archivo.' }
    }
    if (version !== lectura.current) return
    setLeyendo(false)
    setErrores(actual => ({ ...actual, imagen: error }))
    if (error) evento.target.value = ''
  }

  function guardar(evento) {
    evento.preventDefault()
    if (leyendo) return
    const nuevos = {}
    if (!datos.nombre.trim()) nuevos.nombre = 'Ingresa el nombre del producto.'
    else if (datos.nombre.trim().length > 100) nuevos.nombre = 'Usa como máximo 100 caracteres.'
    if (!datos.descripcion.trim()) nuevos.descripcion = 'Ingresa una descripción.'
    else if (datos.descripcion.trim().length > 1000) nuevos.descripcion = 'Usa como máximo 1000 caracteres.'
    if (!categorias.includes(datos.categoria)) nuevos.categoria = 'Selecciona una categoría.'
    if (!/^\d+$/.test(String(datos.precio)) || !Number.isSafeInteger(Number(datos.precio)) || Number(datos.precio) <= 0) nuevos.precio = 'Ingresa un precio entero mayor que cero, en pesos chilenos.'
    if (!/^\d+$/.test(String(datos.stock)) || !Number.isSafeInteger(Number(datos.stock))) nuevos.stock = 'Ingresa un stock entero de cero o más unidades.'
    if (!datos.imagen) nuevos.imagen = 'Agrega una imagen del producto.'
    if (errores.imagen) nuevos.imagen = errores.imagen
    setErrores(nuevos)
    if (Object.keys(nuevos).length) {
      formulario.current.querySelector(`[name="${Object.keys(nuevos)[0]}"]`)?.focus()
      return
    }
    const producto = { ...datos, id: editando || crypto.randomUUID(), nombre: datos.nombre.trim(), descripcion: datos.descripcion.trim(), precio: Number(datos.precio), stock: Number(datos.stock) }
    setProductos(actual => editando ? actual.map(item => item.id === editando ? producto : item) : [...actual, producto])
    setMensaje(`${producto.nombre}: producto ${editando ? 'actualizado' : 'registrado'} en la demostración.`)
    limpiar()
  }

  function campo(nombre, etiqueta, tipo = 'text') {
    return <div className="producto-campo">
      <label htmlFor={`producto-${nombre}`}>{etiqueta}</label>
      <input id={`producto-${nombre}`} name={nombre} type={tipo} value={datos[nombre]} min={nombre === 'precio' ? '1' : '0'} step={tipo === 'number' ? '1' : undefined} required aria-invalid={!!errores[nombre]} aria-describedby={errores[nombre] ? `producto-error-${nombre}` : undefined} onChange={evento => setDatos({ ...datos, [nombre]: evento.target.value })} />
      {errores[nombre] && <span className="producto-error" id={`producto-error-${nombre}`}>{errores[nombre]}</span>}
    </div>
  }

  return <section className="productos-admin" aria-labelledby="productos-titulo">
    <AdminNav />
    <header className="admin-cabecera"><p className="admin-etiqueta">Paraíso del Café / Administración</p><h1 id="productos-titulo">Gestión de productos</h1><p>Registra productos y mantén sus datos, precios e inventario al día.</p></header>
    <div className="admin-demo"><strong>Modo demostración.</strong> Los productos e imágenes solo se guardan en esta pantalla y se restablecen al recargar.</div>
    <div role="status" aria-live="polite">{mensaje && <p className="producto-aviso">{mensaje}</p>}</div>
    <div className="productos-layout">
      <form ref={formulario} className="producto-form" onSubmit={guardar} noValidate aria-labelledby="producto-form-titulo">
        <h2 id="producto-form-titulo">{editando ? 'Editar producto' : 'Registrar producto'}</h2>
        <p className="producto-ayuda">Todos los campos son obligatorios. Precios en CLP.</p>
        {campo('nombre', 'Nombre')}
        <div className="producto-campo"><label htmlFor="producto-descripcion">Descripción</label><textarea id="producto-descripcion" name="descripcion" rows={3} required value={datos.descripcion} aria-invalid={!!errores.descripcion} aria-describedby="producto-error-descripcion" onChange={evento => setDatos({ ...datos, descripcion: evento.target.value })} /><span className="producto-error" id="producto-error-descripcion">{errores.descripcion}</span></div>
        <div className="producto-campo"><label htmlFor="producto-categoria">Categoría</label><select id="producto-categoria" name="categoria" value={datos.categoria} required aria-invalid={!!errores.categoria} aria-describedby="producto-error-categoria" onChange={evento => setDatos({ ...datos, categoria: evento.target.value })}><option value="">Selecciona una categoría</option>{categorias.map(item => <option key={item}>{item}</option>)}</select><span className="producto-error" id="producto-error-categoria">{errores.categoria}</span></div>
        <div className="producto-numeros">{campo('precio', 'Precio (CLP)', 'number')}{campo('stock', 'Stock (unidades)', 'number')}</div>
        <div className="producto-campo"><label htmlFor="producto-imagen">Imagen</label><input ref={archivo} id="producto-imagen" name="imagen" type="file" accept="image/jpeg,image/png,image/webp" aria-invalid={!!errores.imagen} aria-describedby="imagen-ayuda producto-error-imagen" onChange={cargarImagen} /><small id="imagen-ayuda">JPG, PNG o WebP. Máximo 5 MB. Al editar puedes conservar la imagen actual.</small><span className="producto-error" id="producto-error-imagen">{errores.imagen}</span>{datos.imagen && <img className="producto-preview" src={datos.imagen} alt="Vista previa de la imagen del producto" />}</div>
        <div className="producto-form-acciones"><button type="submit" className="primary" disabled={leyendo}>{leyendo ? 'Leyendo imagen…' : editando ? 'Guardar cambios' : 'Registrar producto'}</button><button type="button" onClick={() => { limpiar(); setMensaje(''); formulario.current.querySelector('[name="nombre"]').focus() }}>{editando ? 'Cancelar edición' : 'Limpiar formulario'}</button></div>
      </form>
      <section className="productos-inventario" aria-labelledby="inventario-titulo"><h2 id="inventario-titulo">Productos registrados <small>({productos.length})</small></h2><p className="producto-ayuda">Selecciona un producto para modificar sus datos.</p><div className="productos-items">{productos.map(producto => <article className="producto-resumen" key={producto.id}><img src={producto.imagen} alt={producto.nombre} /><div><small>{producto.categoria}</small><h3>{producto.nombre}</h3><p>{producto.descripcion}</p><strong>{pesos.format(producto.precio)}</strong><p>{producto.stock === 0 ? 'Sin stock' : `${producto.stock} unidades disponibles`}</p><button type="button" aria-label={`Editar producto ${producto.nombre}`} onClick={() => editar(producto)}>Editar</button></div></article>)}</div></section>
    </div>
  </section>
}
