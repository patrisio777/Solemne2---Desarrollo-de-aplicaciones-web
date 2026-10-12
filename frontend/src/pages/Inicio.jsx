import heroImage from '../assets/hero.png';
import cappuccinoImg from '../assets/capuccino.jpg';
import mochaImg from '../assets/mocha.jpg';
import macchiatoImg from '../assets/macchiato.jpg';
import '../inicio.css';

function Inicio() {
  const productos = [
    {
      id: 1,
      name: 'Capuccino',
      price: '$3.800',
      image: cappuccinoImg
    },
    {
      id: 2,
      name: 'Mocha',
      price: '$4.200',
      image: mochaImg
    },
    {
      id: 3,
      name: 'Macchiato',
      price: '$3.500',
      image: macchiatoImg
    }
  ];

  return (
    <>
      <section className="hero">
        <div className="contenedor-hero">
          <div className="hero-content">
            <h1 className="titulo">
              El paraíso a un sorbo.
            </h1>
            <p className="descripcion">
              El café puede ser el elemento fundamental para el día a día, por eso convierte tu vida en un paraíso jugoso y perfecto.
            </p>
            <button className="btn btn-primary">
              Explorar más
            </button>
          </div>

          <div className="imagen-hero">
            <img
              src={heroImage}
              alt="Fotografía del café"
              loading="lazy"
            />
          </div>
        </div>
      </section>

      <section className="productos-destacados">
        <div className="titulo-productos-destacados">
          <h2>Productos Destacados</h2>
        </div>

        <div className="productos-grid">
          {productos.map(product => (
            <article key={product.id} className="tarjeta-producto">
              <div className="imagen-producto">
                <img src={product.image} alt={product.name} />
              </div>
              <h3 className="nombre-producto">{product.name}</h3>
              <div className="contenido-producto">
                <strong className="precio">{product.price}</strong>
                <button className="btn btn-añad-carro">Añadir a carrito</button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

export default Inicio;