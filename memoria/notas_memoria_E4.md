# Textos y capturas para la memoria de la E4

Material listo para pegar en la memoria (E5). Las capturas están en `imagenes/`. Cada apartado
incluye dos o tres frases y el pie de figura que pide el enunciado («Imagen N: título»), que
luego hay que referenciar en el texto.

## 1. Vistas basadas en clases (E4a, opción 2)

Los listados y los detalles de clientes y tarjetas se han reescrito con las vistas genéricas
`ListView` y `DetailView` de Django. Las URLs y las plantillas no cambian: cada vista declara su
`model`, su `template_name` y el nombre del objeto del contexto que espera la plantilla
(`clientes_listado`, `cliente`, `tarjetas_listado` y `tarjeta`). En el detalle del cliente se
mantiene el cálculo del saldo total mediante una anotación en `get_queryset`, y las consultas de
tarjetas siguen trayendo la cuenta asociada con `select_related`.

- Imagen 1: Listado de clientes con `ListView`.
- Imagen 2: Detalle de un cliente con `DetailView` y saldo total.
- Imagen 3: Listado de tarjetas con `ListView`.
- Imagen 4: Detalle de una tarjeta con `DetailView`.

## 2. Filtro de movimientos (E4a, opción 1)

El filtro de movimientos se apoya en el formulario `FiltroMovimientosForm`, que valida el tipo de
movimiento y el rango de fechas antes de consultar la base de datos. La vista construye el
`QuerySet` aplicando únicamente los filtros informados. Si la petición llega por AJAX (jQuery
añade la cabecera `X-Requested-With`), la vista devuelve solo el fragmento HTML del listado,
definido en la plantilla parcial `parciales/resultados_movimientos.html`; si no, devuelve la
página completa, que incluye esa misma plantilla.
En el cliente, siguiendo las recomendaciones del enunciado, se usa jQuery: los selectores se
guardan al cargar la página, la petición se hace con `$.ajax` y, mientras llega la respuesta, la
tabla se atenúa con `fadeTo`; al sustituir las filas, estas aparecen con una animación definida en
CSS. Si algún dato no es válido, el formulario devuelve el error y la tabla no se muestra, y sin
JavaScript el formulario sigue funcionando por GET.

- Imagen 5: Listado de movimientos filtrado por tipo «Gasto».

## 3. Administración personalizada y roles (E4a, opción 4)

Los cuatro modelos tienen personalizada la lista del panel de administración con
`list_display`, `search_fields` y `list_filter`, y los movimientos añaden `date_hierarchy` para
navegar por fechas. Los permisos se reparten en dos grupos definidos en la migración
`0006_roles_movimientos`: «Consulta de movimientos» solo permite ver movimientos, mientras que
«Edición de movimientos» permite ver, añadir, cambiar y borrar. Los usuarios de prueba se crean
con `python manage.py usuarios_roles --password <contraseña>`.

- Imagen 6: Personalización de la lista de movimientos (columnas, búsqueda y filtros).
- Imagen 7: Rol de consulta: solo lectura, sin botones para añadir ni editar.
- Imagen 8: Rol de edición: permite añadir, modificar y borrar movimientos.
- Imagen 9: Búsqueda de movimientos por concepto.

## 4. SPA de contactos con Vue (E4b, 0,5 puntos)

La agenda de contactos es una SPA independiente hecha con Vue 3 que permite mostrar los contactos
(nombre, email y teléfono), crear nuevos y borrarlos. Los contactos añadidos se validan (nombre y
email obligatorios, sin emails duplicados) y la lista se actualiza al momento sin recargar la
página. La página incorpora las tres técnicas de datos estructurados: RDFa en la cabecera,
Microdata en la lista de contactos y un bloque JSON-LD que se regenera con cada alta o borrado.

- Imagen 10: Agenda de contactos con Vue.
- Imagen 11: Alta de un contacto en la agenda.

## Recordatorio de formato de la E5

Según el enunciado: márgenes superior 3,5 cm, inferior 2,5 cm y laterales 2,5 cm; encabezado
«PROYECTO INGENIERIA WEB» en cursiva a la derecha; numeración a la derecha en el pie; portada y
portada interior firmada; resumen y descriptores en la página (i); índices en números romanos
desde la (ii), con índices de tablas y figuras; texto justificado y páginas sin dejar en blanco.
Todas las imágenes y tablas llevan pie y se referencian en el texto.
