# Agenda de contactos (E4b)

SPA de ejemplo para la entrega E4b: agenda que muestra, crea y borra contactos
(nombre, email y teléfono) con Vue 3.

## Cómo ejecutarla

No necesita compilación: Vue se carga desde `vendor/vue.global.prod.js`.

```bash
cd E4b
python3 -m http.server 8088
```

Y abrir <http://localhost:8088/>. También funciona abriendo `index.html` directamente
en el navegador.

## Datos estructurados

La página incluye las tres técnicas de la web semántica:

- **RDFa**: la cabecera marca la aplicación con `vocab="https://schema.org/"` y
  `typeof="WebApplication"`.
- **Microdata**: la lista de contactos usa `ItemList`/`Person` con `itemprop`
  (`name`, `email`, `telephone`).
- **JSON-LD**: el bloque `#datos-estructurados` describe la aplicación y sus contactos,
  y se regenera con cada alta o borrado.
