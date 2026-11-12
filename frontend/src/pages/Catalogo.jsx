import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useProductos, categorias, pesos } from '../productos'
import './Catalogo.css'

function Catalogo() {
  const { productos } = useProductos()
  const [busqueda, setBusqueda] = useState('')
  const [categoria, setCategoria] = useState('')
  const [disponibles, setDisponibles] = useState(false)
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')
  const normalizar = texto => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  const visibles = productos.filter(producto => (!categoria || producto.categoria === categoria) && (!disponibles || producto.stock > 0) && normalizar(`${producto.nombre} ${producto.descripcion}`).includes(normalizar(busqueda.trim())))
  function limpiar() { setBusqueda(''); setCategoria(''); setDisponibles(false) }

  return <section className="catalogo" aria-labelledby="catalogo-titulo">
    <header className="catalogo-cabecera"><div><p className="eyebrow">Paraíso del Café</p><h1 id="catalogo-titulo">Nuestro catálogo</h1><p>Café, sabores y detalles para disfrutar tu próxima pausa.</p></div>{usuario?.es_admin && <Link className="catalogo-primario" to="/admin/productos">Registrar producto</Link>}</header>
    <p className="catalogo-demo">Catálogo de demostración. Las modificaciones del panel se reflejan al navegar y se restablecen al recargar.</p>
    <div className="catalogo-filtros" role="search" aria-label="Buscar productos">
      <div><label htmlFor="catalogo-busqueda">Buscar producto</label><input id="catalogo-busqueda" type="search" placeholder="Nombre o descripción" value={busqueda} onChange={evento => setBusqueda(evento.target.value)} /></div>
      <div><label htmlFor="catalogo-categoria">Categoría</label><select id="catalogo-categoria" value={categoria} onChange={evento => setCategoria(evento.target.value)}><option value="">Todas las categorías</option>{categorias.map(item => <option key={item}>{item}</option>)}</select></div>
      <label className="catalogo-disponibles"><input type="checkbox" checked={disponibles} onChange={evento => setDisponibles(evento.target.checked)} />Solo disponibles</label>
      <button type="button" onClick={limpiar}>Limpiar filtros</button>
    </div>
    <p className="catalogo-conteo" role="status" aria-live="polite">{visibles.length} de {productos.length} productos</p>
    {visibles.length ? <div className="catalogo-grid">{visibles.map(producto => <article className="catalogo-tarjeta" key={producto.id}>
      <Link to={`/producto/${producto.id}`} aria-label={`Consultar ${producto.nombre}`}><img src={producto.imagen} alt={producto.nombre} /></Link>
      <div className="catalogo-tarjeta-cuerpo"><span className="eyebrow">{producto.categoria}</span><h2>{producto.nombre}</h2><p>{producto.descripcion}</p><div className="catalogo-precio"><strong>{pesos.format(producto.precio)}</strong><span>{producto.stock ? `${producto.stock} disponibles` : 'Sin stock'}</span></div><div className="catalogo-acciones"><Link to={`/producto/${producto.id}`}>Ver detalles</Link>{usuario?.es_admin && <Link to={`/admin/productos?editar=${encodeURIComponent(producto.id)}`} aria-label={`Editar producto ${producto.nombre}`}>Editar</Link>}</div></div>
    </article>)}</div> : <div className="catalogo-vacio"><h2>No encontramos productos</h2><p>Prueba con otro nombre o cambia los filtros.</p><button type="button" onClick={limpiar}>Mostrar todos los productos</button></div>}
  </section>
}

export default Catalogo
