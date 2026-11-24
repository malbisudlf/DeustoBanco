const { createApp } = Vue;

createApp({
    data() {
        return {
            contactos: [
                { id: 1, nombre: 'Ana Pérez', email: 'ana.perez@example.com', telefono: '600 111 222' },
                { id: 2, nombre: 'Iker Mendia', email: 'iker.mendia@example.com', telefono: '600 333 444' },
            ],
            nuevo: { nombre: '', email: '', telefono: '' },
            siguienteId: 3,
            aviso: '',
        };
    },
    mounted() {
        this.actualizarJsonLd();
    },
    methods: {
        agregar() {
            const nombre = this.nuevo.nombre.trim();
            const email = this.nuevo.email.trim();

            if (!nombre || !email) {
                this.aviso = 'El nombre y el email son obligatorios.';
                return;
            }
            if (this.contactos.some((contacto) => contacto.email.toLowerCase() === email.toLowerCase())) {
                this.aviso = 'Ese email ya está en la agenda.';
                return;
            }

            this.contactos.push({
                id: this.siguienteId++,
                nombre,
                email,
                telefono: this.nuevo.telefono.trim(),
            });
            this.nuevo = { nombre: '', email: '', telefono: '' };
            this.aviso = '';
            this.actualizarJsonLd();
        },
        borrar(id) {
            this.contactos = this.contactos.filter((contacto) => contacto.id !== id);
            this.aviso = '';
            this.actualizarJsonLd();
        },
        actualizarJsonLd() {
            // JSON-LD con el estado actual de la agenda (web de datos / schema.org).
            const datos = {
                '@context': 'https://schema.org',
                '@type': 'WebApplication',
                name: 'Agenda de contactos',
                applicationCategory: 'BusinessApplication',
                operatingSystem: 'Any',
                description: 'Agenda para mostrar, crear y borrar contactos.',
                mainEntity: {
                    '@type': 'ItemList',
                    numberOfItems: this.contactos.length,
                    itemListElement: this.contactos.map((contacto, indice) => ({
                        '@type': 'ListItem',
                        position: indice + 1,
                        item: {
                            '@type': 'Person',
                            name: contacto.nombre,
                            email: contacto.email,
                            telephone: contacto.telefono,
                        },
                    })),
                },
            };
            document.getElementById('datos-estructurados').textContent = JSON.stringify(datos, null, 2);
        },
    },
}).mount('#app');
