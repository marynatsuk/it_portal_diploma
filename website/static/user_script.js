// FILTER TASKS (USER)
document.addEventListener('DOMContentLoaded', function() {
    const typeCheckboxes = document.querySelectorAll('.type-filter');
    const statusCheckboxes = document.querySelectorAll('.status-filter');
    const tableRows = document.querySelectorAll('#userTableBody tr');
    
    function filterTasks() {
        const selectedTypes = Array.from(typeCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        const selectedStatuses = Array.from(statusCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        
        tableRows.forEach(row => {
            const taskType = row.cells[2].textContent;
            const status = row.cells[6].textContent;
            const typeFilter = selectedTypes.length === 0 || selectedTypes.includes(taskType);
            const statusFilter = selectedStatuses.length === 0 || selectedStatuses.includes(status);
            row.style.display = typeFilter && statusFilter ? '' : 'none';
        });
    }

    typeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });

});

//FILTER REQUESTS (USER)
document.addEventListener('DOMContentLoaded', function() {
    const statusCheckboxes = document.querySelectorAll('.status-filter');
    const tableRows = document.querySelectorAll('#userRequestsTableBody tr');
    
    function filterTasks() {
        const selectedStatuses = Array.from(statusCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        
        tableRows.forEach(row => {
            const status = row.cells[3].textContent;
            const statusFilter = selectedStatuses.length === 0 || selectedStatuses.includes(status);
            row.style.display = statusFilter ? '' : 'none';
        });
    }

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });

});


//FILTER DEVICES (USER)
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('#userDeviceTableBody tr');
    const typeCheckboxes = document.querySelectorAll('.devicetype-filter');
    const brandCheckboxes = document.querySelectorAll('.brand-filter');
    const statusCheckboxes = document.querySelectorAll('.status-filter');
    
    function filterTasks() {
        const selectedTypes = Array.from(typeCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        const selectedBrands = Array.from(brandCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        const selectedStatuses = Array.from(statusCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        
        tableRows.forEach(row => {
            const taskType = row.cells[2].textContent;
            const brand = row.cells[3].textContent; 
            const status = row.cells[5].textContent; 
            const typeFilter = selectedTypes.length === 0 || selectedTypes.includes(taskType);
            const brandFilter = selectedBrands.length === 0 || selectedBrands.includes(brand);
            const statusFilter = selectedStatuses.length === 0 || selectedStatuses.includes(status);
            row.style.display = typeFilter && brandFilter && statusFilter ? '' : 'none';
        });
    }

    typeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });

    brandCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });
    
    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });
});

//FILTER WORKERS (MANAGER)
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('#managerWorkerTableBody tr');
    const typeCheckboxes = document.querySelectorAll('.tasktype-filter');
    
    function filterTasks() {
        const selectedTypes = Array.from(typeCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
    
        tableRows.forEach(row => {
            const taskTypesText = row.cells[6].textContent;
            const taskTypes = taskTypesText.split(',').map(type => type.trim()); 
            console.log(taskTypes)
            const typeFilter = selectedTypes.length === 0 || selectedTypes.some(selectedType => taskTypes.includes(selectedType));
            
            row.style.display = typeFilter ? '' : 'none';
        });
    }

    typeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });
});

//FILTER REQUESTS (MANAGER)
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('#managerRequestTableBody tr');
    const typeCheckboxes = document.querySelectorAll('.type-filter');
    const statusCheckboxes = document.querySelectorAll('.status-filter');
    
    function filterTasks() {
        const selectedTypes = Array.from(typeCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        const selectedStatuses = Array.from(statusCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
        
        tableRows.forEach(row => {
            const taskType = row.cells[2].textContent;
            const status = row.cells[4].textContent;
            const typeFilter = selectedTypes.length === 0 || selectedTypes.includes(taskType);
            const statusFilter = selectedStatuses.length === 0 || selectedStatuses.includes(status);
            row.style.display = typeFilter && statusFilter ? '' : 'none';
        });
    }

    typeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterTasks);
    });
});

