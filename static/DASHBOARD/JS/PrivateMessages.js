function styleUserTable() {
    const table = document.querySelector("#usersTableBody");
    if (!table) return;

    [...table.rows].forEach((row, index) => {
        // Zebra stripe background
        row.style.backgroundColor = index % 2 === 0 ? "#ffffff" : "#f9f9f9";

        // Hover effect
        row.addEventListener("mouseenter", () => {
            row.style.backgroundColor = "#e8f3ff";
            row.style.cursor = "pointer";
        });
        row.addEventListener("mouseleave", () => {
            row.style.backgroundColor = index % 2 === 0 ? "#ffffff" : "#f9f9f9";
        });

        // Style avatar images (if any)
        const img = row.querySelector("img");
        if (img) {
            img.style.width = "32px";
            img.style.height = "32px";
            img.style.borderRadius = "50%";
            img.style.border = "2px solid #ddd";
            img.style.boxShadow = "0 2px 5px rgba(0,0,0,0.1)";
            img.style.transition = "transform 0.2s ease-in-out";
            img.addEventListener("mouseenter", () => img.style.transform = "scale(1.1)");
            img.addEventListener("mouseleave", () => img.style.transform = "scale(1)");
        }

        // Status color badges
        const statusCell = row.cells[3];
        if (statusCell) {
            const text = statusCell.textContent.trim().toLowerCase();
            statusCell.style.fontWeight = "bold";
            statusCell.style.color = text === "active" ? "#0f9d58" : "#d93025";
        }
    });
}

// If your existing JS has a render function for search results
function renderUsers(users) {
    const tbody = document.querySelector("#usersTableBody");
    tbody.innerHTML = "";

    users.forEach(user => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <img src="${user.profile_url}" alt="${user.username}"> ${user.username}
            </td>
            <td>${user.chat_partners}</td>
            <td>${user.last_active}</td>
            <td>${user.status}</td>
            <td><button class="btn btn-primary btn-sm">View</button></td>
        `;
        tbody.appendChild(tr);
    });

    // Apply table design after rendering
    styleUserTable();
}

// Run once on page load (in case table already has rows)
document.addEventListener("DOMContentLoaded", styleUserTable);
