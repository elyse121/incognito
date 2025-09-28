document.addEventListener('DOMContentLoaded', function() {
      // DOM Elements
      const body = document.body;
      const sidebar = document.getElementById('sidebar');
      const mainContent = document.getElementById('mainContent');
      const toggleSidebarBtn = document.getElementById('toggleSidebar');
      const fullscreenBtn = document.getElementById('fullscreenBtn');
      const settingsBtn = document.getElementById('settingsBtn');
      const settingsPanel = document.getElementById('settingsPanel');
      const settingsOverlay = document.getElementById('settingsOverlay');
      const closeSettings = document.getElementById('closeSettings');
      const lightTheme = document.getElementById('lightTheme');
      const darkTheme = document.getElementById('darkTheme');
      const rtlToggle = document.getElementById('rtlToggle');
      const sidebarToggle = document.getElementById('sidebarToggle');
      const rightSidebarToggle = document.getElementById('rightSidebarToggle');
      const logoutBtn = document.querySelector('.logout-btn');

      // Initialize Bootstrap Collapse for dropdowns
      const collapseElements = document.querySelectorAll('[data-bs-toggle="collapse"]');
      collapseElements.forEach(el => {
        el.addEventListener('click', function() {
          const target = document.querySelector(this.getAttribute('href'));
          const isExpanded = this.getAttribute('aria-expanded') === 'true';
          this.setAttribute('aria-expanded', !isExpanded);
          
          // Toggle chevron icon
          const arrow = this.querySelector('.toggle-arrow');
          if (arrow) {
            arrow.classList.toggle('bi-chevron-right');
            arrow.classList.toggle('bi-chevron-down');
          }
        });
      });

      // Toggle sidebar
      toggleSidebarBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        sidebarToggle.checked = sidebar.classList.contains('collapsed');
      });

      // Fullscreen toggle
      fullscreenBtn.addEventListener('click', function() {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(err => {
            console.error(`Error attempting to enable fullscreen: ${err.message}`);
          });
          body.classList.add('fullscreen');
        } else {
          if (document.exitFullscreen) {
            document.exitFullscreen();
            body.classList.remove('fullscreen');
          }
        }
      });

      // Open settings panel
      settingsBtn.addEventListener('click', function() {
        settingsPanel.classList.add('open');
        settingsOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
      });

      // Close settings panel
      closeSettings.addEventListener('click', closeSettingsPanel);
      settingsOverlay.addEventListener('click', closeSettingsPanel);

      function closeSettingsPanel() {
        settingsPanel.classList.remove('open');
        settingsOverlay.classList.remove('active');
        document.body.style.overflow = '';
      }

      // Theme toggle
      lightTheme.addEventListener('click', function() {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
        updateThemeSelection();
      });

      darkTheme.addEventListener('click', function() {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
        updateThemeSelection();
      });

      function updateThemeSelection() {
        const isDarkMode = body.classList.contains('dark-mode');
        lightTheme.classList.toggle('active', !isDarkMode);
        darkTheme.classList.toggle('active', isDarkMode);
      }

      // RTL toggle
      rtlToggle.addEventListener('change', function() {
        if (this.checked) {
          document.documentElement.dir = 'rtl';
        } else {
          document.documentElement.dir = 'ltr';
        }
        localStorage.setItem('rtlMode', this.checked);
      });

      // Sidebar toggle in settings
      sidebarToggle.addEventListener('change', function() {
        sidebar.classList.toggle('collapsed', this.checked);
        localStorage.setItem('sidebarCollapsed', this.checked);
      });

      // Right sidebar toggle
      rightSidebarToggle.addEventListener('change', function() {
        // Add your right sidebar toggle logic here
        console.log('Right sidebar toggle:', this.checked);
        localStorage.setItem('rightSidebar', this.checked);
      });

      // Logout button
      logoutBtn.addEventListener('click', function() {
        // Add your logout logic here
        alert('Logging out...');
      });

      // Initialize from localStorage
      if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
        sidebarToggle.checked = true;
      }

      if (localStorage.getItem('darkMode') === 'true') {
        body.classList.add('dark-mode');
        darkTheme.classList.add('active');
      } else {
        lightTheme.classList.add('active');
      }

      if (localStorage.getItem('rtlMode') === 'true') {
        rtlToggle.checked = true;
        document.documentElement.dir = 'rtl';
      }

      if (localStorage.getItem('rightSidebar') === 'true') {
        rightSidebarToggle.checked = true;
      }

      // Mobile menu toggle (for small screens)
      function checkScreenSize() {
        if (window.innerWidth <= 768) {
          sidebar.classList.add('collapsed');
        } else {
          sidebar.classList.remove('collapsed');
        }
      }

      // Initial check
      checkScreenSize();
      
      // Check on resize
      window.addEventListener('resize', checkScreenSize);

      // Tooltip functionality
      const tooltipElements = document.querySelectorAll('.header-icon-btn, .user-avatar');
      tooltipElements.forEach(el => {
        const tooltip = el.querySelector('.tooltip');
        if (tooltip) {
          el.addEventListener('mouseenter', () => {
            tooltip.style.opacity = '1';
          });
          el.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
          });
        }
      });
    });

  
    // Enhanced Search Functionality
    document.addEventListener('DOMContentLoaded', function() {
      const globalSearch = document.getElementById('globalSearch');
      const searchButton = document.getElementById('searchButton');
      let currentSearchTerm = '';
      
      // Create no results message element
      const noResultsMsg = document.createElement('div');
      noResultsMsg.className = 'search-no-results';
      noResultsMsg.textContent = 'No results found';
      document.querySelector('.dashboard-content').appendChild(noResultsMsg);
      
      // Function to perform search
      function performSearch(searchTerm) {
        currentSearchTerm = searchTerm.trim().toLowerCase();
        
        if (!currentSearchTerm) {
          clearSearchHighlights();
          noResultsMsg.style.display = 'none';
          return;
        }
        
        // Get all text nodes in the main content area
        const mainContent = document.querySelector('.main-content');
        const walker = document.createTreeWalker(
          mainContent,
          NodeFilter.SHOW_TEXT,
          null,
          false
        );
        
        let foundResults = false;
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
          if (node.parentNode.classList && 
              (node.parentNode.classList.contains('search-highlight') || 
               node.parentNode.classList.contains('search-no-results'))) {
            continue;
          }
          textNodes.push(node);
        }
        
        clearSearchHighlights();
        
        textNodes.forEach(textNode => {
          const content = textNode.nodeValue;
          const parent = textNode.parentNode;
          
          if (content.toLowerCase().includes(currentSearchTerm)) {
            foundResults = true;
            const regex = new RegExp(currentSearchTerm, 'gi');
            const newContent = content.replace(regex, match => {
              return `<span class="search-highlight">${match}</span>`;
            });
            
            if (parent.innerHTML) {
              parent.innerHTML = parent.innerHTML.replace(
                content, 
                newContent
              );
            } else {
              const span = document.createElement('span');
              span.innerHTML = newContent;
              parent.replaceChild(span, textNode);
            }
          }
        });
        
        noResultsMsg.style.display = foundResults ? 'none' : 'block';
      }
      
      // Clear search highlights
      function clearSearchHighlights() {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
          const parent = highlight.parentNode;
          parent.textContent = parent.textContent;
          parent.normalize();
        });
      }
      
      // Event listeners for search
      globalSearch.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
          performSearch(this.value);
        } else if (this.value.trim() === '') {
          clearSearchHighlights();
          noResultsMsg.style.display = 'none';
        }
      });
      
      searchButton.addEventListener('click', function() {
        performSearch(globalSearch.value);
      });
      
      // Add this to your existing dark mode toggle
      function updateSearchForDarkMode(isDarkMode) {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
          highlight.style.color = isDarkMode ? '#000' : '#000';
          highlight.style.backgroundColor = isDarkMode ? '#FFEB3B' : '#FFEB3B';
        });
      }
      
      // Modify your existing theme toggle to include search updates
      lightTheme.addEventListener('click', function() {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
        updateThemeSelection();
        updateSearchForDarkMode(false);
      });
      
      darkTheme.addEventListener('click', function() {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
        updateThemeSelection();
        updateSearchForDarkMode(true);
      });
    });