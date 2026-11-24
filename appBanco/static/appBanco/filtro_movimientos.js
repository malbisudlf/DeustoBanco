(() => {
    const formulario = document.querySelector("#filtro-movimientos");
    const resultados = document.querySelector("#resultados-movimientos");
    const estado = document.querySelector("#estado-movimientos");
    let peticionActiva;

    formulario.addEventListener("change", () => formulario.requestSubmit());

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        peticionActiva?.abort();
        const control = new AbortController();
        peticionActiva = control;
        const url = new URL(formulario.action);
        for (const [nombre, valor] of new FormData(formulario)) {
            if (valor) {
                url.searchParams.set(nombre, valor);
            }
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

            const errores = nuevosResultados.querySelector(".errores-filtro-movimientos");
            const cantidad = nuevosResultados.querySelectorAll("[data-movimiento]").length;
            resultados.replaceChildren(...nuevosResultados.childNodes);
            for (const campo of formulario.querySelectorAll("[name]")) {
                const idError = `${campo.id}_error`;
                if (document.getElementById(idError)) {
                    campo.setAttribute("aria-invalid", "true");
                    campo.setAttribute("aria-describedby", idError);
                } else {
                    campo.removeAttribute("aria-invalid");
                    campo.removeAttribute("aria-describedby");
                }
            }
            if (errores) {
                estado.textContent = "Revisa los filtros para buscar movimientos.";
            } else {
                estado.textContent = cantidad === 1
                    ? "1 movimiento encontrado."
                    : `${cantidad} movimientos encontrados.`;
            }
        } catch {
            if (!control.signal.aborted) {
                estado.textContent = "No se pudo actualizar el listado. Pulsa «Aplicar filtros» para reintentar.";
            }
        } finally {
            if (peticionActiva === control) {
                resultados.removeAttribute("aria-busy");
                peticionActiva = undefined;
            }
        }
    });
})();
