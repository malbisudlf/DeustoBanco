# DeustoBanco — Proyecto de Ingeniería Web (E4)

Repositorio de la entrega E4 del proyecto web colaborativo. La estructura está pensada para que
el comprimido de entrega (`IW-<grupo>-E4.zip`) se genere directamente desde el repositorio.

```
.
├── E4a/      Proyecto Django (E4a): funcionalidades añadidas sobre DeustoBanco
├── E4b/      SPA de contactos con Vue (E4b)
└── memoria/  Textos y capturas para la memoria (E5)
```

## Proyectos

- **E4a** — Django. Instrucciones en [`E4a/README.md`](E4a/README.md).
- **E4b** — Vue. Instrucciones en [`E4b/README.md`](E4b/README.md).

## Generar el comprimido de entrega

```bash
zip -r IW-<grupo>-E4.zip . -x '.git/*' -x '*/ing_web/*' -x '*/db.sqlite3'
```
