
//FILTER OF TABLE ON /ADMIN/ADMIN_DASHBOARD
document.addEventListener('DOMContentLoaded', function() {
    const departmentCheckboxes = document.querySelectorAll('.department-filter');
    const roleCheckboxes = document.querySelectorAll('.role-filter');
    const tableRows = document.querySelectorAll('#adminUserTable tr');

    function filterTable() {
        console.log("Filtering table");        const departmentsChecked = Array.from(departmentCheckboxes).some(checkbox => checkbox.checked);
        const rolesChecked = Array.from(roleCheckboxes).some(checkbox => checkbox.checked);
    
        tableRows.forEach(row => {
            const department = row.querySelector('.department');
            const role = row.querySelector('.role');
            if (department && role) {
                const departmentText = department.textContent.trim();
                const roleText = role.textContent.trim();
    
                const departmentFilter = !departmentsChecked || Array.from(departmentCheckboxes).some(checkbox => checkbox.checked && checkbox.value === departmentText);
                const roleFilter = !rolesChecked || Array.from(roleCheckboxes).some(checkbox => checkbox.checked && checkbox.value === roleText);
    
                row.style.display = departmentFilter && roleFilter ? '' : 'none';
            } else {
                row.style.display = ''; 
            }
        });
    }
    
    departmentCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            filterTable();
        });
    });
    
    roleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            filterTable();
        });
    });
    
});

