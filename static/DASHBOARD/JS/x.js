document.addEventListener('DOMContentLoaded', function() {
      // Sample data
      
      
      const conversations = {
        "1-2": [
          {sender: 1, text: "Hey, are you free tomorrow?", time: "Today, 14:30"},
          {sender: 2, text: "Yes, what time works for you?", time: "Today, 14:32"},
          {sender: 1, text: "How about 3 PM at the café?", time: "Today, 14:33"}
        ],
        "1-3": [
          {sender: 1, text: "Did you finish the project?", time: "Yesterday, 10:15"},
          {sender: 3, text: "Almost done! Sending it tonight.", time: "Yesterday, 10:20"}
        ],
        "2-5": [
          {sender: 2, text: "Please refund my money!", time: "Jul 30, 22:05"},
          {sender: 5, text: "I already sent it, check your account", time: "Jul 30, 22:10"}
        ]
      };
      
      // DOM elements
      const usersTableBody = document.getElementById('usersTableBody');
      const partnersContainer = document.getElementById('partnersContainer');
      const searchInput = document.getElementById('searchInput');
      const searchBtn = document.getElementById('searchBtn');
      const noUsersResults = document.getElementById('noUsersResults');
      const noPartnersResults = document.getElementById('noPartnersResults');
      
      // Current state
      let currentView = 'users'; // 'users' or 'partners'
      let currentUserId = null;
      let currentSearchTerm = '';
      
      // Initialize the app
      function initApp() {
        renderUsersList(usersData);
        setupEventListeners();
      }
      
      // Render users list
      function renderUsersList(users) {
        usersTableBody.innerHTML = '';
        
        if (users.length === 0) {
          noUsersResults.classList.remove('d-none');
          return;
        }
        
        noUsersResults.classList.add('d-none');
        
        users.forEach(user => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>
              <div class="d-flex align-items-center gap-3">
                <img src="${user.avatar}" class="user-avatar">
                <span class="fw-bold">${user.name}</span>
              </div>
            </td>
            <td>
              <span class="badge bg-light text-dark">${user.partnersCount} partners</span>
            </td>
            <td>${user.lastActive}</td>
            <td>
              <span class="badge ${getStatusBadgeClass(user.status)}">
                ${user.status.charAt(0).toUpperCase() + user.status.slice(1)}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-outline-primary action-btn view-partners-btn" 
                      data-user-id="${user.id}" 
                      data-user-name="${user.name}">
                <i class="fas fa-eye"></i> View Partners
              </button>
              <button class="btn btn-sm btn-outline-danger action-btn">
                <i class="fas fa-ban"></i> Ban
              </button>
            </td>
          `;
          usersTableBody.appendChild(row);
        });
      }
      
      // Render partners list
      function renderPartnersList(userId) {
        const user = usersData.find(u => u.id == userId);
        if (!user) return;
        
        document.getElementById('selectedUserName').textContent = user.name;
        partnersContainer.innerHTML = '';
        
        let filteredPartners = user.partners;
        if (currentSearchTerm) {
          filteredPartners = user.partners.filter(partner => 
            partner.name.toLowerCase().includes(currentSearchTerm.toLowerCase())
          );
        }
        
        if (filteredPartners.length === 0) {
          noPartnersResults.classList.remove('d-none');
          return;
        }
        
        noPartnersResults.classList.add('d-none');
        
        filteredPartners.forEach(partner => {
          const partnerCard = document.createElement('div');
          partnerCard.className = `col-md-6 partner-card ${partner.status === 'reported' ? 'reported' : ''}`;
          partnerCard.innerHTML = `
            <div class="card mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="d-flex align-items-center gap-3">
                    <img src="${partner.avatar}" class="user-avatar">
                    <div>
                      <h6 class="mb-1 fw-bold">${partner.name}</h6>
                      <small class="text-muted">Last chat: ${partner.lastChat}</small>
                    </div>
                  </div>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary view-chat-btn" 
                            data-user1="${userId}" 
                            data-user2="${partner.id}"
                            data-user1-name="${user.name}"
                            data-user2-name="${partner.name}">
                      <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger">
                      <i class="fas fa-ban"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `;
          partnersContainer.appendChild(partnerCard);
        });
      }
      
      // Get status badge class
      function getStatusBadgeClass(status) {
        switch(status) {
          case 'active': return 'bg-success';
          case 'reported': return 'bg-warning text-dark';
          case 'banned': return 'badge-banned';
          default: return 'bg-secondary';
        }
      }
      
      // Search functionality
      function performSearch() {
        currentSearchTerm = searchInput.value.trim();
        
        if (currentView === 'users') {
          const filteredUsers = usersData.filter(user => 
            user.name.toLowerCase().includes(currentSearchTerm.toLowerCase())
          );
          renderUsersList(filteredUsers);
        } else if (currentView === 'partners' && currentUserId) {
          renderPartnersList(currentUserId);
        }
      }
      
      // Setup event listeners
      function setupEventListeners() {
        // Search button click
        searchBtn.addEventListener('click', performSearch);
        
        // Search on Enter key
        searchInput.addEventListener('keyup', function(e) {
          if (e.key === 'Enter') performSearch();
        });
        
        // View partners button
        document.addEventListener('click', function(e) {
          if (e.target.closest('.view-partners-btn')) {
            const btn = e.target.closest('.view-partners-btn');
            currentUserId = parseInt(btn.getAttribute('data-user-id'));
            currentView = 'partners';
            
            document.querySelector('.user-table').classList.add('d-none');
            document.getElementById('partnersPanel').classList.remove('d-none');
            
            renderPartnersList(currentUserId);
          }
        });
        
        // Back to users list
        document.getElementById('backToUsersBtn').addEventListener('click', function() {
          currentView = 'users';
          document.querySelector('.user-table').classList.remove('d-none');
          document.getElementById('partnersPanel').classList.add('d-none');
          renderUsersList(
            currentSearchTerm 
              ? usersData.filter(user => user.name.toLowerCase().includes(currentSearchTerm.toLowerCase()))
              : usersData
          );
        });
        
        // View conversation modal
        document.addEventListener('click', function(e) {
          if (e.target.closest('.view-chat-btn')) {
            const btn = e.target.closest('.view-chat-btn');
            const user1Id = btn.getAttribute('data-user1');
            const user2Id = btn.getAttribute('data-user2');
            const user1Name = btn.getAttribute('data-user1-name');
            const user2Name = btn.getAttribute('data-user2-name');
            
            document.getElementById('user1Name').textContent = user1Name;
            document.getElementById('user2Name').textContent = user2Name;
            
            // Load conversation
            const conversationContainer = document.getElementById('conversationContainer');
            conversationContainer.innerHTML = '';
            
            const conversationKey = `${Math.min(user1Id, user2Id)}-${Math.max(user1Id, user2Id)}`;
            const messages = conversations[conversationKey] || [];
            
            messages.forEach(msg => {
              const isSender = msg.sender == user1Id;
              const bubble = document.createElement('div');
              bubble.className = `chat-bubble ${isSender ? 'sender' : 'receiver'}`;
              bubble.innerHTML = `
                <strong>${isSender ? user1Name : user2Name}</strong> (${msg.time})<br>
                ${msg.text}
                <div class="message-actions">
                  <div class="dropdown">
                    <button class="btn btn-sm btn-link text-muted p-0" data-bs-toggle="dropdown">
                      <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu">
                      <li><a class="dropdown-item" href="#"><i class="fas fa-trash me-2"></i>Delete message</a></li>
                    </ul>
                  </div>
                </div>
              `;
              conversationContainer.appendChild(bubble);
            });
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('conversationModal'));
            modal.show();
          }
        });
      }
      
      // Initialize the application
      initApp();
    });