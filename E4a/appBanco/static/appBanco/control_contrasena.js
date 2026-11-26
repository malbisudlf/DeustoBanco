const plantillaControl = document.querySelector("#control-contrasena");

for (const campo of document.querySelectorAll(".formulario input[type='password']")) {
    const contenedor = document.createElement("span");
    contenedor.className = "campo-contrasena";

    const boton = plantillaControl.content.firstElementChild.cloneNode(true);
    const nombre = campo.name === "password2" ? "confirmación de contraseña" : "contraseña";
    boton.setAttribute("aria-controls", campo.id);
    boton.setAttribute("aria-label", `Mostrar ${nombre}`);
    boton.title = `Mostrar ${nombre}`;

    campo.before(contenedor);
    contenedor.append(campo, boton);

    boton.addEventListener("click", () => {
        const mostrar = campo.type === "password";
        campo.type = mostrar ? "text" : "password";
        boton.setAttribute("aria-pressed", String(mostrar));
        boton.title = `${mostrar ? "Ocultar" : "Mostrar"} ${nombre}`;
    });
}
