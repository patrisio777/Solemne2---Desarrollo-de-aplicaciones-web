import { Link } from 'react-router-dom';
import heroImage from '../assets/hero.png';
import { useProductos, pesos } from '../productos';
import '../inicio.css';

function Inicio() {
  const { productos: inventario } = useProductos();
  const productos = inventario.slice(0, 3).map(producto => ({
    id: producto.id, name: producto.nombre, price: pesos.format(producto.precio), image: producto.imagen
  }));

  return (
    <>
      <section className="hero">
        <div className="contenedor-hero">
          <div className="imagen-hero">
            <img src={heroImage} alt="Fotografía del café" />
          </div>
          <div className="hero-content">
            <div className="hero-texto">
              <h1 className="titulo">EL PARAÍSO A UN SORBO.</h1>
              <p className="descripcion">
                El café puede ser el elemento fundamental para el día a día, por eso convierte tu vida en un paraíso jugoso y perfecto.
              </p>
            </div>
            <Link to="/catalogo" className="btn btn-primary btn-hero">Ver más</Link>
          </div>
        </div>
      </section>

      <section className="productos-destacados">
        <div className="titulo-productos-destacados">
          <h2>PRODUCTOS DESTACADOS</h2>
        </div>

        <div className="productos-grid">
          {productos.map(product => (
            <article key={product.id} className="tarjeta-producto">
              <h3 className="nombre-producto">{product.name}</h3>

              <div className="imagen-producto">
                <img src={product.image} alt={product.name} />
              </div>

              <div className="fila-producto">
                <strong className="precio">{product.price}</strong>
                <button className="btn-producto">Añadir a carrito</button>
              </div>

              <Link to={`/producto/${product.id}`} className="ver-detalles">
                Ver detalles
              </Link>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

export default Inicio;
