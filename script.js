// Auto-dismiss alerts after 3 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 3000);
});

// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const required = form.querySelectorAll('[required]');
            let valid = true;
            required.forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please fill all required fields!');
            }
        });
    });
});

// Live clock in dashboard
function updateClock() {
    const clock = document.getElementById('clock');
    if (clock) {
        const now = new Date();
        clock.textContent = now.toLocaleString();
    }
}
setInterval(updateClock, 1000);