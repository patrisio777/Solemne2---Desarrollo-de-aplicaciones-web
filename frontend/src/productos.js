import { createContext, useContext } from 'react'
import capuccino from './assets/capuccino.jpg'
import mocha from './assets/mocha.jpg'
import macchiato from './assets/macchiato.jpg'

export const categorias = ['Café', 'Repostería', 'Accesorios']
export const productosIniciales = [
  { id: '1', nombre: 'Capuccino', descripcion: 'Espresso con leche y una suave capa de espuma.', categoria: 'Café', precio: 3800, stock: 20, imagen: capuccino },
  { id: '2', nombre: 'Mocha', descripcion: 'Café con chocolate y leche.', categoria: 'Café', precio: 4200, stock: 0, imagen: mocha },
  { id: '3', nombre: 'Macchiato', descripcion: 'Espresso intenso con un delicado toque de espuma de leche.', categoria: 'Café', precio: 3500, stock: 15, imagen: macchiato },
]
export const pesos = new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' })
export const ProductosContext = createContext(null)
export const useProductos = () => useContext(ProductosContext)
