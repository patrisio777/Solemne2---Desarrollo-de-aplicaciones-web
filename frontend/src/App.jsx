import { Routes, Route } from 'react-router-dom'
import Inicio from './pages/Inicio'
import Catalogo from './pages/Catalogo'
import DetalleProducto from './pages/DetalleProducto'
import Carrito from './pages/Carrito'
import Login from './pages/Login'
import Registro from './pages/Registro'
import Pago from './pages/Pago'
import Confirmacion from './pages/Confirmacion'
import Contacto from './pages/Contacto'
import QuienesSomos from './pages/QuienesSomos'
import NoEncontrada from './pages/NoEncontrada'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/catalogo" element={<Catalogo />} />
      <Route path="/producto/:id" element={<DetalleProducto />} />
      <Route path="/carrito" element={<Carrito />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/pago" element={<Pago />} />
      <Route path="/confirmacion" element={<Confirmacion />} />
      <Route path="/contacto" element={<Contacto />} />
      <Route path="/quienes-somos" element={<QuienesSomos />} />
      <Route path="*" element={<NoEncontrada />} />
    </Routes>
  )
}

export default App