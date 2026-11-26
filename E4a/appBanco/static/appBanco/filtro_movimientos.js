(() => {
    // jQuery se usa por recomendación del enunciado: selectores sencillos, AJAX corto
    // y efectos de carga. Sin JavaScript, el formulario sigue funcionando por GET.
    const $formulario = $("#filtro-movimientos");
    const $resultados = $("#resultados-movimientos");
    const $estado = $("#estado-movimientos");
    let peticion = null;

    function marcarErroresAccesibles() {
        $formulario.find(":input[name]").each((indice, campo) => {
            const $campo = $(campo);
            const idError = `${campo.id}_error`;
            if (document.getElementById(idError)) {
                $campo.attr({ "aria-invalid": "true", "aria-describedby": idError });
            } else {
                $campo.removeAttr("aria-invalid").removeAttr("aria-describedby");
            }
        });
    }

    function mostrarResumen(hayErrores, cantidad) {
        if (hayErrores) {
            $estado.text("Revisa los filtros para buscar movimientos.");
        } else if (cantidad === 1) {
            $estado.text("1 movimiento encontrado.");
        } else {
            $estado.text(`${cantidad} movimientos encontrados.`);
        }
    }

    $formulario.on("change", () => {
        $formulario.trigger("submit");
    });

    $formulario.on("submit", (evento) => {
        evento.preventDefault();
        if (peticion) {
            peticion.abort();
        }

        const datos = {};
        $formulario.serializeArray().forEach(({ name, value }) => {
            if (value) {
                datos[name] = value;
            }
        });

        $estado.text("Cargando movimientos…");
        $resultados.attr("aria-busy", "true").stop(true, true).fadeTo(150, 0.55);

        const actual = $.ajax({
            url: $formulario.attr("action"),
            data: datos,
            dataType: "html",
        });
        peticion = actual;

        actual
            .done((fragmento) => {
                // La vista responde solo con el fragmento de la tabla (o la lista de errores).
                $resultados.html(fragmento).addClass("actualizado");
                marcarErroresAccesibles();
                mostrarResumen(
                    $resultados.find(".errores-filtro-movimientos").length > 0,
                    $resultados.find("[data-movimiento]").length,
                );
            })
            .fail((xhr, motivo) => {
                if (motivo !== "abort") {
                    $estado.text("No se pudo actualizar el listado. Pulsa «Aplicar filtros» para reintentar.");
                }
            })
            .always(() => {
                if (peticion !== actual) {
                    return;
                }
                peticion = null;
                $resultados.removeAttr("aria-busy").stop(true, true).fadeTo(200, 1);
            });
    });
})();
