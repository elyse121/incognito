document.addEventListener('DOMContentLoaded', function() {
      // Sample data
      const reportsData = [
        {
          id: "RPT-78945",
          reportedUser: {
            id: 1,
            name: "Mike Brown",
            avatar: "https://i.pravatar.cc/150?img=8",
            status: "banned"
          },
          reporter: {
            id: 2,
            name: "Jane Smith",
            avatar: "https://i.pravatar.cc/150?img=11",
            status: "active"
          },
          message: {
            text: "You'll regret ignoring me. I know where you live and I'll make sure you pay for this.",
            time: "Today, 14:25",
            context: [
              {
                sender: 2,
                text: "I'm not interested, please stop messaging me.",
                time: "Today, 14:20"
              },
              {
                sender: 1,
                text: "Why not? Give me a chance, I know you like me.",
                time: "Today, 14:22"
              }
            ]
          },
          report: {
            date: "Today, 14:30",
            category: "harassment",
            reason: "This user sent me offensive messages after I rejected their advances. The language used was inappropriate and made me uncomfortable.",
            status: "pending",
            priority: "high"
          }
        },
        {
          id: "RPT-78944",
          reportedUser: {
            id: 3,
            name: "Alex Johnson",
            avatar: "https://i.pravatar.cc/150?img=3",
            status: "active"
          },
          reporter: {
            id: 4,
            name: "Sarah Miller",
            avatar: "https://i.pravatar.cc/150?img=4",
            status: "active"
          },
          message: {
            text: "Check out this amazing opportunity to make $1000/day with no work! Click here: scamlink.com",
            time: "Today, 09:15",
            context: []
          },
          report: {
            date: "Today, 09:20",
            category: "spam",
            reason: "This is clearly a scam message trying to steal personal information.",
            status: "pending",
            priority: "medium"
          }
        },
        {
          id: "RPT-78940",
          reportedUser: {
            id: 5,
            name: "David Lee",
            avatar: "https://i.pravatar.cc/150?img=12",
            status: "active"
          },
          reporter: {
            id: 6,
            name: "Emma Wilson",
            avatar: "https://i.pravatar.cc/150?img=9",
            status: "active"
          },
          message: {
            text: "Your work is terrible and you should be fired immediately.",
            time: "Yesterday, 16:45",
            context: [
              {
                sender: 6,
                text: "I've finished the project draft, please review when you have time.",
                time: "Yesterday, 16:40"
              }
            ]
          },
          report: {
            date: "Yesterday, 16:50",
            category: "harassment",
            reason: "Unprofessional and abusive language in a work group chat.",
            status: "resolved",
            priority: "high"
          }
        }
      ];
      
      // DOM elements
      const reportsContainer = document.getElementById('reportsContainer');
      const searchInput = document.getElementById('searchInput');
      const searchBtn = document.getElementById('searchBtn');
      const filterSelect = document.getElementById('filterSelect');
      const noResults = document.getElementById('noResults');
      
      // Render reports
      function renderReports(reports) {
        reportsContainer.innerHTML = '';
        
        if (reports.length === 0) {
          noResults.classList.remove('d-none');
          return;
        }
        
        noResults.classList.add('d-none');
        
        reports.forEach(report => {
          const reportCard = document.createElement('div');
          reportCard.className = `col-md-6 report-card ${report.report.status === 'resolved' ? 'resolved' : ''}`;
          reportCard.innerHTML = `
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <span class="report-tag ${getTagClass(report.report.category)} me-2">${report.report.category}</span>
                    <span class="badge ${report.report.status === 'pending' ? 'bg-warning' : 'bg-success'}">
                      ${report.report.status}
                    </span>
                  </div>
                  <small class="text-muted">${report.report.date}</small>
                </div>
                
                <div class="d-flex align-items-center gap-3 mb-3">
                  <img src="${report.reportedUser.avatar}" class="user-avatar">
                  <div>
                    <h6 class="mb-0">${report.reportedUser.name}</h6>
                    <small class="text-muted">Reported by ${report.reporter.name}</small>
                  </div>
                </div>
                
                <p class="message-preview mb-3">${report.message.text}</p>
                
                <p class="report-reason mb-3"><strong>Reason:</strong> "${report.report.reason}"</p>
                
                <div class="d-flex justify-content-between align-items-center">
                  <button class="btn btn-sm btn-outline-primary view-report-btn" 
                          data-report-id="${report.id}"
                          data-bs-toggle="modal" 
                          data-bs-target="#reportModal">
                    <i class="fas fa-eye me-1"></i> Review
                  </button>
                  <div>
                    ${report.report.status === 'pending' ? `
                    <button class="btn btn-sm btn-outline-success resolve-btn me-1">
                      <i class="fas fa-check me-1"></i> Resolve
                    </button>
                    ` : ''}
                    <button class="btn btn-sm btn-outline-danger">
                      <i class="fas fa-trash me-1"></i> Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `;
          reportsContainer.appendChild(reportCard);
        });
      }
      
      // Get tag class based on category
      function getTagClass(category) {
        switch(category.toLowerCase()) {
          case 'harassment': return 'tag-harassment';
          case 'spam': return 'tag-spam';
          case 'inappropriate': return 'tag-inappropriate';
          default: return 'tag-other';
        }
      }
      
      // Filter reports
      function filterReports() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        const filterValue = filterSelect.value;
        
        let filteredReports = reportsData;
        
        // Apply status filter
        if (filterValue !== 'all') {
          filteredReports = filteredReports.filter(report => 
            filterValue === 'pending' ? report.report.status === 'pending' :
            filterValue === 'resolved' ? report.report.status === 'resolved' :
            report.report.category === filterValue
          );
        }
        
        // Apply search filter
        if (searchTerm) {
          filteredReports = filteredReports.filter(report => 
            report.reportedUser.name.toLowerCase().includes(searchTerm) ||
            report.reporter.name.toLowerCase().includes(searchTerm) ||
            report.message.text.toLowerCase().includes(searchTerm) ||
            report.report.reason.toLowerCase().includes(searchTerm)
          );
        }
        
        renderReports(filteredReports);
      }
      
      // Event listeners
      searchBtn.addEventListener('click', filterReports);
      searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') filterReports();
      });
      filterSelect.addEventListener('change', filterReports);
      
      // Initialize
      renderReports(reportsData);
    });