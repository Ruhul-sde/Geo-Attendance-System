
// Admin JavaScript

// Handle approve and reject buttons
document.addEventListener('DOMContentLoaded', function() {
    // Approve leave
    const approveButtons = document.querySelectorAll('.approve-btn');
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const empId = this.getAttribute('data-emp-id');
            const leaveId = this.getAttribute('data-leave-id');
            updateLeaveStatus(empId, leaveId, 'approved');
        });
    });
    
    // Reject leave
    const rejectButtons = document.querySelectorAll('.reject-btn');
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const empId = this.getAttribute('data-emp-id');
            const leaveId = this.getAttribute('data-leave-id');
            updateLeaveStatus(empId, leaveId, 'rejected');
        });
    });
});

// Function to update leave status
function updateLeaveStatus(employeeId, leaveId, status) {
    fetch('/admin/update_leave', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            employee_id: employeeId,
            leave_id: leaveId,
            status: status
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Reload page to reflect changes
            window.location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch((error) => {
        alert('Error: ' + error.message);
    });
}
document.addEventListener('DOMContentLoaded', function() {
    // Handle approve button clicks
    document.querySelectorAll('.approve-btn').forEach(button => {
        button.addEventListener('click', function() {
            updateLeaveStatus(this.dataset.empId, this.dataset.leaveId, 'approved');
        });
    });

    // Handle reject button clicks
    document.querySelectorAll('.reject-btn').forEach(button => {
        button.addEventListener('click', function() {
            updateLeaveStatus(this.dataset.empId, this.dataset.leaveId, 'rejected');
        });
    });

    // Function to send status update to server
    function updateLeaveStatus(employeeId, leaveId, status) {
        fetch('/admin/update_leave', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                employee_id: employeeId,
                leave_id: leaveId,
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                // Remove the leave row or refresh the page
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the leave status.');
        });
    }
});
// Admin panel JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Leave approval/rejection functionality
    const approveButtons = document.querySelectorAll('.approve-btn');
    const rejectButtons = document.querySelectorAll('.reject-btn');
    
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const empId = this.dataset.empId;
            const leaveId = this.dataset.leaveId;
            
            if (confirm('Are you sure you want to approve this leave request?')) {
                approveLeave(empId, leaveId);
            }
        });
    });
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const empId = this.dataset.empId;
            const leaveId = this.dataset.leaveId;
            
            if (confirm('Are you sure you want to reject this leave request?')) {
                rejectLeave(empId, leaveId);
            }
        });
    });
    
    function approveLeave(empId, leaveId) {
        fetch(`/admin/approve_leave/${empId}/${leaveId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the row or update its appearance
                const row = document.querySelector(`button[data-emp-id="${empId}"][data-leave-id="${leaveId}"]`).closest('tr');
                row.style.backgroundColor = '#d4edda';
                setTimeout(() => {
                    row.remove();
                    
                    // Check if there are no more rows for this employee
                    const employeeSection = row.closest('.employee-leaves');
                    const remainingRows = employeeSection.querySelectorAll('tbody tr');
                    if (remainingRows.length === 0) {
                        employeeSection.remove();
                    }
                    
                    // Check if there are no more leave requests
                    const allEmployeeSections = document.querySelectorAll('.employee-leaves');
                    if (allEmployeeSections.length === 0) {
                        document.querySelector('.card').innerHTML = '<p>No pending leave applications.</p>';
                    }
                }, 500);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the request.');
        });
    }
    
    function rejectLeave(empId, leaveId) {
        fetch(`/admin/reject_leave/${empId}/${leaveId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the row or update its appearance
                const row = document.querySelector(`button[data-emp-id="${empId}"][data-leave-id="${leaveId}"]`).closest('tr');
                row.style.backgroundColor = '#f8d7da';
                setTimeout(() => {
                    row.remove();
                    
                    // Check if there are no more rows for this employee
                    const employeeSection = row.closest('.employee-leaves');
                    const remainingRows = employeeSection.querySelectorAll('tbody tr');
                    if (remainingRows.length === 0) {
                        employeeSection.remove();
                    }
                    
                    // Check if there are no more leave requests
                    const allEmployeeSections = document.querySelectorAll('.employee-leaves');
                    if (allEmployeeSections.length === 0) {
                        document.querySelector('.card').innerHTML = '<p>No pending leave applications.</p>';
                    }
                }, 500);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the request.');
        });
    }
});
