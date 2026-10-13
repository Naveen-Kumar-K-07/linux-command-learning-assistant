/* ===================================================================
   Linux Commands Learning Assistant — Main JavaScript
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss or manual dismiss for flash alerts
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });


    // Auto-initialize progress bars from data-progress attribute (eliminates CSS inline syntax warnings)
    document.querySelectorAll('.progress-fill[data-progress]').forEach(bar => {
        const val = parseFloat(bar.dataset.progress) || 0;
        bar.style.width = val + '%';
    });
});
