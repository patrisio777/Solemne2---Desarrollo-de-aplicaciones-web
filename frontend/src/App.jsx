import { useEffect, useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import './layout.css'
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
import Admin from './pages/Admin'
import AdminProductos from './pages/AdminProductos'
import NoEncontrada from './pages/NoEncontrada'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import RutaAdmin from './components/RutaAdmin'
import { ProductosContext, productosIniciales } from './productos'

function App() {
  const [productos, setProductos] = useState(productosIniciales)
  const [tema, setTema] = useState(() => {
    const guardado = localStorage.getItem('tema')
    return ['claro', 'oscuro', 'vintage', 'pastel'].includes(guardado) ? guardado : 'claro'
  })
  useEffect(() => { localStorage.setItem('tema', tema) }, [tema])
  const { pathname, search } = useLocation()
  const panel = pathname === '/admin' || pathname.startsWith('/admin/') || pathname.startsWith('/demo/admin')
  return (
    <ProductosContext.Provider value={{ productos, setProductos }}>
    <div className="store site-shell admin-shell" data-theme={tema}>
      <Navbar tema={tema} onTemaChange={setTema} />
      <main className={panel || pathname === '/' ? undefined : 'site-page'}>
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
          <Route path="/admin" element={<RutaAdmin><Admin tema={tema} /></RutaAdmin>} />
          <Route path="/demo/admin" element={<Admin demo tema={tema} />} />
          <Route path="/admin/productos" element={<RutaAdmin><AdminProductos key={pathname + search} /></RutaAdmin>} />
          <Route path="/demo/admin/productos" element={<AdminProductos key={pathname + search} />} />
          <Route path="*" element={<NoEncontrada />} />
        </Routes>
      </main>
      <Footer />
    </div>
    </ProductosContext.Provider>
  )
}

export default App
