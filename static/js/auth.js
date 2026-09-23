// ---------------- API REQUEST HELPER ----------------
async function apiRequest(url, options = {}) {
    try {
        const token = localStorage.getItem("dhyeya_token") || localStorage.getItem("access_token");

        options.headers = {
            "Content-Type": "application/json",
            ...options.headers,
            ...(token && { Authorization: `Bearer ${token}` })
        };

        const response = await fetch(`${url}`, options);
        
        // Handling 401: Unauthorized / Token Expired
        if (response.status === 401) {
            console.error("Session Expired or Invalid Token");
            localStorage.removeItem("dhyeya_token");
            localStorage.removeItem("access_token");
            window.location.href = "/login";
            return;
        }

        const text = await response.text();
        const data = text ? JSON.parse(text) : {};

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong");
        }

        return data;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

// ---------------- DASHBOARD DATA FETCH ----------------
async function loadDashboardSummary() {
    try {
        // Correct prefix match with backend API
        const data = await apiRequest("/api/dashboard/summary");
        if (!data) return;

        // Populate elements safely
        if (document.getElementById("uploads-count")) {
            document.getElementById("uploads-count").innerText = data.uploads_count ?? 0;
        }
        if (document.getElementById("questions-count")) {
            document.getElementById("questions-count").innerText = data.questions_count ?? 0;
        }
        if (document.getElementById("bookmarks-count")) {
            document.getElementById("bookmarks-count").innerText = data.bookmarks_count ?? 0;
        }
        if (document.getElementById("notes-count")) {
            document.getElementById("notes-count").innerText = data.notes_count ?? 0;
        }
    } catch (err) {
        console.log("Could not load summary data:", err);
    }
}

// Page load event
document.addEventListener("DOMContentLoaded", () => {
    // Sirf jab Dashboard Page par hon tabhi call run karein
    if (window.location.pathname.includes("dashboard")) {
        loadDashboardSummary();
    }
});