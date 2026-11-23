(() => {
    const filtro = document.querySelector("#tipo-movimiento");
    const resultados = document.querySelector("#resultados-movimientos");
    const estado = document.querySelector("#estado-movimientos");
    const sinResultados = document.querySelector("#sin-resultados-movimientos");
    let peticionActiva;
    let tipoAplicado = filtro.value;

    filtro.addEventListener("change", async () => {
        peticionActiva?.abort();
        const control = new AbortController();
        peticionActiva = control;
        const tipo = filtro.value;
        const url = new URL(filtro.dataset.url, window.location.origin);
        if (tipo) {
            url.searchParams.set("tipo", tipo);
        }

        estado.textContent = "Cargando movimientos…";
        resultados.setAttribute("aria-busy", "true");

        try {
            const respuesta = await fetch(url, { signal: control.signal });
            if (!respuesta.ok) {
                throw new Error(`HTTP ${respuesta.status}`);
            }

            const pagina = new DOMParser().parseFromString(await respuesta.text(), "text/html");
            const nuevosResultados = pagina.querySelector("#resultados-movimientos");
            if (!nuevosResultados) {
                throw new Error("La respuesta no contiene el listado de movimientos.");
            }
            if (control.signal.aborted) {
                return;
            }

            // El listado actual sirve para probar la interfaz antes de añadir el filtro en Django.
            const filas = Array.from(nuevosResultados.querySelectorAll("tr[data-tipo]"));
            const coincidencias = filas.filter((fila) => !tipo || fila.dataset.tipo === tipo);
            if (coincidencias.length) {
                resultados.replaceChildren(...coincidencias);
            } else {
                resultados.replaceChildren(sinResultados.content.cloneNode(true));
            }
            tipoAplicado = tipo;
            estado.textContent = coincidencias.length === 1
                ? "1 movimiento encontrado."
                : `${coincidencias.length} movimientos encontrados.`;
        } catch (error) {
            if (control.signal.aborted) {
                return;
            }
            filtro.value = tipoAplicado;
            estado.textContent = "No se pudo actualizar el listado. Vuelve a seleccionar el filtro para reintentar.";
        } finally {
            if (peticionActiva === control) {
                resultados.removeAttribute("aria-busy");
                peticionActiva = undefined;
            }
        }
    });

    document.querySelector("#filtro-movimientos").hidden = false;
})();
