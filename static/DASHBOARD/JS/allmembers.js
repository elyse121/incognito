document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-status-btn').forEach(button => {
    button.addEventListener('click', async () => {
      const memberId = button.getAttribute('data-member-id');
      try {
        const response = await fetch(`/dashboard/toggle-status/${memberId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          }
        });
        const data = await response.json();
        if (data.success) {
          // Refresh the page after success
          location.reload();
        } else {
          alert('Failed to toggle status: ' + (data.error || 'Unknown error'));
        }
      } catch (error) {
        alert('Error toggling status: ' + error);
      }
    });
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
