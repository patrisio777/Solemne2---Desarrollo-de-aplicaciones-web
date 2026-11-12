# TaskCampus - Equipo Cafeinómanos

Laboratorio final de React del ramo Desarrollo de Aplicaciones Web. Partimos del proyecto base que nos pasaron y lo terminamos como un gestor de tareas: carga las tareas desde JSONPlaceholder y se pueden crear, completar, editar, eliminar, filtrar y buscar.

Integrantes:
- Jose Arguello
- Patricio Chaug
- Javiera Fuentealba
- Brandon Valdés
- Cristobal Garrido
- Gabriel Moreno

## Versiones

Lo trabajamos con Node v24.21.0 y npm 11.19.0. El proyecto usa React 19 y Vite 8, las versiones exactas están en el package-lock.json.

## Cómo correrlo

```
git clone https://github.com/PatricioChaugsix/TaskCampus-TeamCafeinomanos.git
cd TaskCampus-TeamCafeinomanos
npm install
npm run dev
```

Se abre en http://localhost:5173. Para compilar:

```
npm run build
npm run preview
```

Si están en Windows y PowerShell no deja correr npm (error de "ejecución de scripts deshabilitada"), usen `npm.cmd install` y `npm.cmd run dev`, o abran la terminal en CMD.

## Estructura

```
src/
  main.jsx
  App.jsx                 maneja la vista activa, el modal de eliminar y los mensajes
  App.css, index.css
  components/
    Header.jsx
    Navigation.jsx        botones Resumen / Tareas / Nueva tarea
    TaskSummary.jsx       contadores
    TaskFilters.jsx       filtro por estado + buscador
    TaskList.jsx
    TaskItem.jsx          una tarea (estado, edición con doble clic, botones)
    TaskForm.jsx          formulario para crear
    Button.jsx            botón reutilizable
    Modal.jsx             modal de confirmación
  views/
    SummaryView.jsx
    TasksView.jsx
    NewTaskView.jsx
  hooks/
    useTareas.js          estado de las tareas, filtros y operaciones
  services/
    tareasService.js      los fetch a la API
```

Seguimos la separación del tutorial 12. Los componentes muestran datos y avisan cuando pasa algo, App coordina, useTareas tiene el estado y las operaciones, y tareasService es el único que hace fetch.

## Vistas

En Resumen se ven el total de tareas, las pendientes, las completadas y cuántas se están mostrando con el filtro que esté puesto. Tareas tiene los filtros, el buscador y la lista (ahí se completa, se edita con doble clic y se elimina). Nueva tarea tiene el formulario; si la tarea se crea bien te lleva a la lista con un mensaje.

El header y la navegación están en las tres.

## Limitaciones de la API

JSONPlaceholder no guarda nada. Responde como si hubiera creado o editado, pero si recargan la página vuelven las mismas 10 tareas. Los cambios duran mientras la página esté abierta, aunque se cambie de vista. No usamos localStorage.

También nos pasó esto: al crear una tarea la API siempre devuelve id 201, y ese recurso no existe en el servidor. Entonces si uno intenta completar o editar una tarea creada en la sesión, el PUT da error 500. Decidimos mostrar el error y dejar la tarea como estaba en vez de hacer como que funcionó. Eliminarla sí funciona porque el DELETE responde 200 con cualquier id. Las pruebas de PUT y DELETE las hicimos con las tareas que vienen del GET.

## Qué cambiamos respecto a la base

| Elemento | Cómo venía | Cómo quedó |
|---|---|---|
| App | Total fijo de 3 y un alert | Coordina vistas, modal y mensajes con el hook |
| TaskList | 3 tareas escritas a mano y botones con alert | Lista con map y key, más mensaje si no hay resultados |
| TaskSummary | Un número que llegaba por props | Total, pendientes, completadas y mostradas, calculados |
| ActionButton | Ejecutaba una función por props | Lo cambiamos por Button, que se usa en la lista, los filtros, el formulario, el modal y el resumen |
| Estilos | Contenedor, tarjetas, lista y botones | Agregamos navegación, filtros, buscador, etiquetas de estado, formulario, mensajes, modal y vista para celular. Sacamos los style en línea de los componentes |
| Datos | Arreglo de textos fijo | Tareas con id, idRemoto, titulo y completada que vienen de la API |

## Investigación

### Navegación entre vistas

No usamos React Router, no se pedía y no queríamos meter otra dependencia. En App hay un `useState('resumen')` para la vista activa. Navigation recibe esa vista y la función para cambiarla, y cada botón manda 'resumen', 'tareas' o 'nueva'. App muestra la vista que toca con renderizado condicional. Como las tareas y los filtros están en useTareas (que se usa en App), no se pierden cuando una vista se desmonta.

Fuentes: https://react.dev/learn/conditional-rendering y https://react.dev/learn/sharing-state-between-components

Archivos: App.jsx, Navigation.jsx

Para probarlo: en Tareas poner el filtro Pendientes y buscar algo, ir a Resumen y volver. El filtro y la búsqueda siguen puestos.

### Estado derivado

En estado guardamos solo lo que no se puede calcular: las tareas, el filtro y el texto de búsqueda. La lista que se muestra y los contadores se calculan en cada render en useTareas (tareasVisibles y contadores). Si los tuviéramos en otro useState habría que actualizarlos a mano cada vez y se podrían desincronizar.

Fuentes: https://react.dev/learn/choosing-the-state-structure (la parte de "Avoid redundant state") y el tutorial 08

Archivos: useTareas.js, TaskSummary.jsx

Para probarlo: crear, completar o eliminar una tarea y mirar que el resumen y la lista cambian al tiro.

### Actualización funcional del estado

Cuando el estado nuevo depende del anterior usamos `setTareas(prev => ...)`. Así se trabaja siempre sobre la última versión aunque React todavía no haya actualizado la variable. Además siempre creamos arreglos y objetos nuevos (`[nueva, ...prev]`, `prev.map` con `{ ...t }`, `prev.filter`), nunca modificamos el arreglo que había.

Fuentes: https://react.dev/reference/react/useState#updating-state-based-on-the-previous-state y https://react.dev/learn/updating-arrays-in-state

Archivos: useTareas.js (crearTarea, alternarEstado, editarTitulo y eliminarTarea)

Para probarlo: completar una tarea, editar otra y eliminar una tercera, una tras otra. Quedan las tres aplicadas.

### Identificadores y API simulada

Cada tarea tiene dos ids. `id` es el de la interfaz, el que se usa como key y para saber qué tarea modificar. `idRemoto` es el que se le manda a la API. En las tareas del GET los dos son iguales. En las que creamos, `id` sale de `Date.now()` e `idRemoto` es lo que devuelve el POST (siempre 201). Si hubiéramos usado el 201 como key, dos tareas creadas tendrían la misma. Cuando una petición falla no se toca el estado y el mensaje de error dice qué tarea fue, así ninguna otra cambia sin que uno se entere.

Fuentes: https://jsonplaceholder.typicode.com/guide/ y https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key

Archivos: useTareas.js, tareasService.js

Para probarlo: crear dos tareas seguidas, aparecen las dos y la consola no reclama por keys repetidas. Después intentar completar una de ellas: sale el error 500 y no cambia ninguna otra.

## Pruebas

Las hicimos en Chrome con npm run dev.

| Caso | Pasos | Esperado | Obtenido | Evidencia |
|---|---|---|---|---|
| RF01 carga inicial | Abrir la app | 10 tareas de la API | Salen 10 y el resumen dice total 10 | Vistas Tareas y Resumen |
| RF11 error al cargar | Cambiar la URL de la API por una mala y recargar | Mensaje de error | "Error al obtener las tareas de la API (código 404)". Después dejamos la URL bien de nuevo | Mensaje rojo arriba |
| RF03 crear | Nueva tarea, escribir "Tarea nueva uno", Agregar | POST y la tarea aparece sin recargar | Aparece primera, con "Tarea creada correctamente." | Lista |
| RF04 crear vacía | Escribir solo espacios y Agregar | No se guarda y avisa | "El minimo del titulo es de 3 caracteres." | Debajo del formulario |
| RF04 editar vacía | Doble clic, borrar todo, Enter | No se guarda y avisa | "Mínimo 3 caracteres." al lado del campo | Lista |
| RF05 cambiar estado | Completar | Cambia la tarea, el filtro y el resumen | Queda completada y tachada, el resumen sube en 1 | Lista y Resumen |
| RF06 editar con Enter | Doble clic, cambiar título, Enter | Guarda el título | Quedó "Titulo editado por Enter" | Lista |
| RF06 editar con blur | Doble clic, cambiar título, clic afuera | Guarda el título | Quedó "Titulo editado por blur" | Lista |
| RF07 cancelar eliminar | Eliminar y Cancelar | La tarea sigue | Sigue | Lista |
| RF07 confirmar eliminar | Eliminar y Confirmar | DELETE y sale de la lista | Pasó de 10 a 9 | Lista |
| RF08 filtros | Completadas y después Pendientes | Solo las de ese estado | 4 completadas y 6 pendientes | Lista |
| RF09 búsqueda | Pendientes y buscar "QUI" | Junta filtro y texto, sin importar mayúsculas | 4 pendientes que tienen "qui" | Lista |
| RF11 sin resultados | Buscar "zzzz" | Aviso de que no hay | "Ninguna tarea coincide con el filtro o la búsqueda." | Lista |
| RF10 resumen | Con Pendientes + "qui" ir a Resumen | Total distinto de mostradas | Total 10, pendientes 6, completadas 4, mostradas 4 | Resumen |
| RF12 operación en curso | Completar y mirar los botones | Se bloquean mientras responde | Quedan deshabilitados con "Sincronizando..." y vuelven | Lista |
| RF13 navegación | Pasar por las tres vistas | Sin recargar ni perder nada | Filtro y búsqueda siguen al volver | Las tres vistas |
| Ids de tareas nuevas | Crear "Tarea nueva uno" y "Tarea nueva dos" | Las dos, sin keys repetidas | Salen las dos y la consola no reclama | Lista y consola |
| Error en tarea nueva | Completar "Tarea nueva dos" | Avisa y no cambia nada | Error 500 de la API, la tarea sigue pendiente | Mensaje rojo |

## Paraíso del Café

El frontend de la cafetería está en `frontend/`. Incluye la tabla de usuarios, el formulario de productos, el catálogo y los cuatro temas del sprint 1.

Para iniciarlo:

```sh
cd frontend
npm ci
npm run dev
```

En desarrollo, el acceso de demostración es `admin1` / `admin1`. Los datos de demostración se restablecen al recargar. Consulta también [la documentación de la cafetería](README-paraiso-del-cafe.md).
