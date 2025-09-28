document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const postsTable = document.getElementById('postsTable');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const statusFilter = document.getElementById('statusFilter');
    const postDetailModal = new bootstrap.Modal(document.getElementById('postDetailModal'));
    const postDetailContent = document.getElementById('postDetailContent');
    const commentsContent = document.getElementById('commentsContent');

    // postsData comes from Django context
    // Ensure this is defined in your template: <script> const postsData = {{ posts_data|safe }}; </script>

    // Initialize page
    renderPosts(postsData);
    setupEventListeners();

    // Render posts table
    function renderPosts(posts) {
        postsTable.innerHTML = '';

        posts.forEach((post, index) => {
            const row = document.createElement('tr');

            // Handle avatar safely
            let avatar = 'https://i.pravatar.cc/150';
            if (post.author.avatar) avatar = post.author.avatar;

            // Handle media (photo)
            let mediaHTML = '<span class="text-muted">None</span>';
            if (post.photo) mediaHTML = `<img src="${post.photo}" class="post-image" style="max-width:120px;">`;

            // Determine status
            let status = post.status || 'active';
            const statusClass = getStatusClass(status);

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>
                    <div class="d-flex align-items-center gap-2">
                        <img src="${avatar}" class="user-avatar">
                        <span>${post.author.name || post.author.username}</span>
                    </div>
                </td>
                <td><div class="post-content">${post.content}</div></td>
                <td>${mediaHTML}</td>
                <td>${post.created_at}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        ${status.charAt(0).toUpperCase() + status.slice(1)}
                    </span>
                </td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary action-btn view-post-btn" data-post-id="${post.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${status === 'reported' ? `
                        <button class="btn btn-sm btn-outline-danger action-btn">
                            <i class="fas fa-ban"></i>
                        </button>
                        ` : ''}
                        <button class="btn btn-sm btn-outline-secondary action-btn">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                    </div>
                </td>
            `;
            postsTable.appendChild(row);
        });
    }

    // Status badge classes
    function getStatusClass(status) {
        switch(status) {
            case 'active': return 'badge-active';
            case 'reported': return 'badge-reported';
            case 'pending': return 'badge-warning';
            case 'archived': return 'badge-archived';
            default: return '';
        }
    }

    // Setup event listeners
    function setupEventListeners() {
        // Search
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') performSearch();
        });
        statusFilter.addEventListener('change', performSearch);

        // View post modal
        document.addEventListener('click', function(e) {
            if (e.target.closest('.view-post-btn')) {
                const postId = parseInt(e.target.closest('.view-post-btn').getAttribute('data-post-id'));
                const post = postsData.find(p => p.id === postId);
                showPostDetail(post);
            }
        });
    }

    // Search posts
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusFilterValue = statusFilter.value;

        let filteredPosts = postsData;

        if (statusFilterValue !== 'all') {
            filteredPosts = filteredPosts.filter(post => post.status === statusFilterValue);
        }

        if (searchTerm) {
            filteredPosts = filteredPosts.filter(post =>
                post.content.toLowerCase().includes(searchTerm) ||
                (post.author.name && post.author.name.toLowerCase().includes(searchTerm)) ||
                (post.author.username && post.author.username.toLowerCase().includes(searchTerm))
            );
        }

        renderPosts(filteredPosts);
    }

    // Show post detail modal
    function showPostDetail(post) {
        let avatar = 'https://i.pravatar.cc/150';
        if (post.author.avatar) avatar = post.author.avatar;

        let mediaHTML = '';
        if (post.photo) mediaHTML = `<div class="mb-3"><img src="${post.photo}" class="img-fluid rounded"></div>`;

        const statusClass = getStatusClass(post.status || 'active');

        postDetailContent.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <div class="d-flex align-items-center mb-3">
                        <img src="${avatar}" class="user-avatar me-3">
                        <div>
                            <h5 class="mb-0">${post.author.name || post.author.username}</h5>
                            <small class="text-muted">Posted on ${post.created_at}</small>
                        </div>
                    </div>
                    <div class="mb-3"><p>${post.content}</p></div>
                    ${mediaHTML}
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header"><h6 class="mb-0">Post Details</h6></div>
                        <div class="card-body">
                            <div class="mb-3">
                                <h6>Status</h6>
                                <span class="status-badge ${statusClass}">${(post.status || 'Active').charAt(0).toUpperCase() + (post.status || 'Active').slice(1)}</span>
                            </div>
                            <div class="mb-3">
                                <h6>Post ID</h6>
                                <span>#POST-${post.id.toString().padStart(4,'0')}</span>
                            </div>
                            ${post.reports && post.reports > 0 ? `
                            <div>
                                <h6>Reports</h6>
                                <span>${post.reports} report(s)</span>
                            </div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        postDetailModal.show();
    }

});
