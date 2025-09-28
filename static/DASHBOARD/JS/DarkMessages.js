// Sample data
    const darkRoomsData = [
      {
        id: 1,
        token: "XK-8943-JF12",
        participants: [
          { id: 1, name: "John Doe", avatar: "https://i.pravatar.cc/150?img=5" },
          { id: 2, name: "Jane Smith", avatar: "https://i.pravatar.cc/150?img=11" }
        ],
        created: "Today, 09:14",
        lastActivity: "2 mins ago",
        messages: [
          { sender: 1, text: "Did you get the documents I sent?", time: "Today, 09:15" },
          { sender: 2, text: "Yes, everything looks good. Let's proceed", time: "Today, 09:16" },
          { sender: 1, text: "Perfect. I'll transfer the funds tomorrow", time: "Today, 09:17" }
        ]
      },
      {
        id: 2,
        token: "PL-5621-KD34",
        participants: [
          { id: 3, name: "Alex Johnson", avatar: "https://i.pravatar.cc/150?img=3" },
          { id: 4, name: "Mike Brown", avatar: "https://i.pravatar.cc/150?img=8" }
        ],
        created: "Today, 10:30",
        lastActivity: "15 mins ago",
        messages: [
          { sender: 3, text: "Are we still meeting at the usual place?", time: "Today, 10:31" },
          { sender: 4, text: "Yes, 8pm. Don't be late this time", time: "Today, 10:33" },
          { sender: 3, text: "I'll be there. Bring the package", time: "Today, 10:34" }
        ]
      },
      {
        id: 3,
        token: "QW-7890-RT56",
        participants: [
          { id: 5, name: "Emma Wilson", avatar: "https://i.pravatar.cc/150?img=9" },
          { id: 2, name: "Jane Smith", avatar: "https://i.pravatar.cc/150?img=11" }
        ],
        created: "Yesterday, 22:15",
        lastActivity: "1 hour ago",
        messages: []
      },
      {
        id: 4,
        token: "MN-3456-TY78",
        participants: [
          { id: 2, name: "Jane Smith", avatar: "https://i.pravatar.cc/150?img=11" },
          { id: 6, name: "David Lee", avatar: "https://i.pravatar.cc/150?img=12" }
        ],
        created: "Today, 11:45",
        lastActivity: "30 mins ago",
        messages: [
          { sender: 2, text: "The documents are ready for review", time: "Today, 11:46" },
          { sender: 6, text: "I'll check them and get back to you", time: "Today, 11:50" }
        ]
      }
    ];

    // DOM elements
    const darkRoomsTable = document.getElementById('darkRoomsTable');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const timeFilter = document.getElementById('timeFilter');
    const topParticipants = document.getElementById('topParticipants');
    const newRoomsCount = document.getElementById('newRoomsCount');
    const messagesCount = document.getElementById('messagesCount');
    const activeRoomsCount = document.getElementById('activeRoomsCount');

    // Initialize the page
    document.addEventListener('DOMContentLoaded', function() {
      renderDarkRooms(darkRoomsData);
      renderTopParticipants();
      updateStats();
    });

    // Render dark rooms table
    function renderDarkRooms(rooms) {
      darkRoomsTable.innerHTML = '';
      
      rooms.forEach((room, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${index + 1}</td>
          <td><span class="token-badge">${room.token}</span></td>
          <td>
            <div class="d-flex gap-3">
              ${room.participants.map(participant => `
                <div class="participant-card">
                  <img src="${participant.avatar}" class="user-avatar">
                  <p class="user-name">${participant.name}</p>
                </div>
              `).join('')}
            </div>
          </td>
          <td>${room.created}</td>
          <td>${room.lastActivity}</td>
          <td>
            <button class="btn btn-sm btn-primary view-btn" data-bs-toggle="collapse" data-bs-target="#chatDetails${room.id}">
              <i class="fas fa-eye me-1"></i> View
            </button>
          </td>
        `;
        
        const detailsRow = document.createElement('tr');
        detailsRow.className = 'collapse';
        detailsRow.id = `chatDetails${room.id}`;
        detailsRow.innerHTML = `
          <td colspan="6" style="background-color: #f8f9fa; padding: 0;">
            <div class="chat-container">
              <div class="chat-header">
                <strong>Token: ${room.token}</strong> 
                <span class="ms-2">(${room.participants.map(p => p.name).join(' ↔ ')})</span>
              </div>
              ${room.messages.length > 0 ? 
                room.messages.map(msg => {
                  const participant = room.participants.find(p => p.id === msg.sender);
                  return `
                    <div class="message-bubble ${index % 2 === 0 ? 'sent' : 'received'}">
                      <div class="message-sender">${participant.name}</div>
                      <p>${msg.text}</p>
                      <div class="message-time">${msg.time}</div>
                    </div>
                  `;
                }).join('') : `
                <div class="no-messages">
                  <i class="fas fa-comment-slash fa-2x mb-3"></i>
                  <h5>No Messages Found</h5>
                  <p class="text-muted">This dark room has no message history</p>
                </div>
              `}
            </div>
          </td>
        `;
        
        darkRoomsTable.appendChild(row);
        darkRoomsTable.appendChild(detailsRow);
      });
    }

    // Render top participants
    function renderTopParticipants() {
      // Count participant activity
      const participantCounts = {};
      darkRoomsData.forEach(room => {
        room.participants.forEach(participant => {
          if (!participantCounts[participant.id]) {
            participantCounts[participant.id] = {
              ...participant,
              count: 0
            };
          }
          participantCounts[participant.id].count++;
        });
      });

      // Sort by most active
      const sortedParticipants = Object.values(participantCounts)
        .sort((a, b) => b.count - a.count)
        .slice(0, 3);

      // Render to DOM
      topParticipants.innerHTML = sortedParticipants.map(participant => `
        <div class="list-group-item border-0 d-flex align-items-center">
          <img src="${participant.avatar}" class="user-avatar me-3">
          <div class="flex-grow-1">
            <h6 class="mb-0">${participant.name}</h6>
            <small class="text-muted">${participant.count} active rooms</small>
          </div>
          <span class="badge bg-primary rounded-pill">${participant.count} today</span>
        </div>
      `).join('');
    }

    // Update statistics
    function updateStats() {
      const todayRooms = darkRoomsData.filter(room => room.created.includes('Today'));
      const totalMessages = darkRoomsData.reduce((sum, room) => sum + room.messages.length, 0);
      
      newRoomsCount.textContent = todayRooms.length;
      messagesCount.textContent = totalMessages;
      activeRoomsCount.textContent = darkRoomsData.filter(room => room.lastActivity.includes('min') || room.lastActivity.includes('hour')).length;
    }

    // Search functionality
    function performSearch() {
      const searchTerm = searchInput.value.toLowerCase();
      const timeFilterValue = timeFilter.value;
      
      let filteredRooms = darkRoomsData;
      
      // Apply time filter
      if (timeFilterValue === 'today') {
        filteredRooms = filteredRooms.filter(room => room.created.includes('Today'));
      } else if (timeFilterValue === 'week') {
        // In a real app, you'd have proper date filtering
        filteredRooms = filteredRooms.filter(room => 
          room.created.includes('Today') || 
          room.created.includes('Yesterday') ||
          room.created.includes('days ago')
        );
      } else if (timeFilterValue === 'month') {
        filteredRooms = filteredRooms; // Show all for this demo
      }
      
      // Apply search filter
      if (searchTerm) {
        filteredRooms = filteredRooms.filter(room => 
          room.token.toLowerCase().includes(searchTerm) ||
          room.participants.some(p => p.name.toLowerCase().includes(searchTerm))
        );
      }
      
      renderDarkRooms(filteredRooms);
      
      // Highlight search results
      if (searchTerm) {
        document.querySelectorAll('.user-name, .token-badge').forEach(el => {
          const text = el.textContent.toLowerCase();
          if (text.includes(searchTerm)) {
            const regex = new RegExp(searchTerm, 'gi');
            el.innerHTML = el.textContent.replace(regex, match => 
              `<span class="search-highlight">${match}</span>`
            );
          }
        });
      }
    }

    // Event listeners
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keyup', function(e) {
      if (e.key === 'Enter') performSearch();
    });
    timeFilter.addEventListener('change', performSearch);