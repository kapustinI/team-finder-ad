// Header sidebar toggle logic
(function(){
  document.addEventListener("DOMContentLoaded", function() {
    const userMenu = document.querySelector('.user-menu');
    const sidebar = document.getElementById('userSidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!userMenu || !sidebar || !overlay) return;

    function openSidebar() {
      sidebar.classList.add('show');
      overlay.classList.add('show');
      sidebar.setAttribute('aria-hidden', 'false');
    }

    function closeSidebar() {
      sidebar.classList.remove('show');
      overlay.classList.remove('show');
      sidebar.setAttribute('aria-hidden', 'true');
    }

    userMenu.addEventListener('click', (e) => {
      e.stopPropagation();
      if (sidebar.classList.contains('show')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && sidebar.classList.contains('show')) {
        closeSidebar();
      }
    });

    document.addEventListener('click', (e) => {
      const isClickInside = sidebar.contains(e.target) || userMenu.contains(e.target);
      if (!isClickInside && sidebar.classList.contains('show')) {
        closeSidebar();
      }
    });
  });
})();
