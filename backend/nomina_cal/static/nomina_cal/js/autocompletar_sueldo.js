document.addEventListener('DOMContentLoaded', function () {
    const empleadoSelect = document.getElementById('id_empleado');
    const sueldoInput = document.getElementById('id_sueldo_base');

    if (!empleadoSelect || !sueldoInput) return;

    empleadoSelect.addEventListener('change', function () {
        const empleadoId = this.value;
        if (!empleadoId) return;

        fetch(`/nomina_cal/ajax/obtener-salario/?empleado_id=${empleadoId}`)
            .then(response => response.json())
            .then(data => {
                if (data.salario) {
                    sueldoInput.value = data.salario.toFixed(0);
                    sueldoInput.style.backgroundColor = '#e8f8f5';
                } else {
                    sueldoInput.value = 0;
                    sueldoInput.style.backgroundColor = '#f9ebea';
                }
            })
            .catch(error => console.error('Error al obtener salario:', error));
    });
});
