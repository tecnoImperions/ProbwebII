document.addEventListener("DOMContentLoaded", function() {
    const draggables = document.querySelectorAll('.draggable');
    const dropzones = document.querySelectorAll('.dropzone');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', e => {
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', e => {
            draggable.classList.remove('dragging');
        });
    });

    dropzones.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            const dragging = document.querySelector('.dragging');
            zone.appendChild(dragging);
        });

        zone.addEventListener('drop', e => {
            e.preventDefault();
            const dragging = document.querySelector('.dragging');
            const id = dragging.getAttribute('data-id');
            const estado = zone.id;

            // Actualizar en base de datos
            fetch(`/update_estado/${id}/${estado}`, {
                method: 'POST'
            })
            .then(res => res.json())
            .then(data => {
                if(data.success){
                    console.log(`Producto ${id} movido a ${estado}`);
                } else {
                    alert('Error al actualizar estado');
                }
            });
        });
    });
});
