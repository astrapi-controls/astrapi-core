// Mobile sidebar management for HTMX navigation

window.htmxCloseMobileSidebar = function() {
    if (window.innerWidth < 1024) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (document.body) document.body.classList.remove('mobile-sidebar-open');
    }
}

// Auto-close mobile sidebar after HTMX navigation
document.addEventListener('htmx:afterSwap', function(e) {
    if (e.target && e.target.id === 'main-content') {
        htmxCloseMobileSidebar();
    }
});
