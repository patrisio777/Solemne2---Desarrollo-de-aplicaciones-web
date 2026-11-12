import { Link, useParams } from 'react-router-dom'
import { useProductos, pesos } from '../productos'
import './Catalogo.css'

function DetalleProducto() {
  const { id } = useParams()
  const { productos } = useProductos()
  const producto = productos.find(item => item.id === id)
  const usuario = JSON.parse(localStorage.getItem('usuario') || 'null')
  if (!producto) return <section className="catalogo catalogo-vacio"><h1>Producto no encontrado</h1><p>El producto solicitado no está disponible en este catálogo.</p><Link to="/catalogo">Volver al catálogo</Link></section>
  return <section className="catalogo" aria-labelledby="detalle-titulo"><Link to="/catalogo">← Volver al catálogo</Link><article className="catalogo-detalle"><img src={producto.imagen} alt={producto.nombre} /><div><p className="eyebrow">{producto.categoria}</p><h1 id="detalle-titulo">{producto.nombre}</h1><p>{producto.descripcion}</p><strong className="detalle-precio">{pesos.format(producto.precio)}</strong><p>{producto.stock ? `${producto.stock} unidades disponibles` : 'Sin stock'}</p>{usuario?.es_admin && <Link className="catalogo-primario" to={`/admin/productos?editar=${encodeURIComponent(producto.id)}`}>Editar producto</Link>}<p className="catalogo-demo">Producto de demostración. Precio expresado en pesos chilenos.</p></div></article></section>
}

export default DetalleProducto
