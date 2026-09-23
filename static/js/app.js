console.log("APP JS LOADED");

async function startUpload() {
    console.log("START UPLOAD CLICKED");

    const form = document.getElementById("uploadForm");
    const uploadButton = document.getElementById("uploadBtn");
    const questionList = document.getElementById("questionList");

    const token = localStorage.getItem("dhyeya_token");

    if (!token) {
        alert("Please login first.");
        window.location.href = "login.html";
        return;
    }

    const formData = new FormData(form);
    const exam = formData.get("exam");
    const subject = formData.get("subject");
    const year = formData.get("year");
    const fileInput = form.querySelector('input[type="file"]');
    const file = fileInput ? fileInput.files[0] : null;

    if (!exam || !subject || !year || !file) {
        alert("Please fill all fields and select a file.");
        return;
    }

    const uploadURL = `http://127.0.0.1:8000/upload?exam=${encodeURIComponent(exam)}&subject=${encodeURIComponent(subject)}&year=${encodeURIComponent(year)}`;
    const sendFormData = new FormData();
    sendFormData.append("file", file);

    try {
        uploadButton.disabled = true;
        uploadButton.innerText = "Uploading...";

        if (questionList) {
            questionList.innerHTML = `<div class="card" style="padding: 15px;"><p>Processing file... Please wait.</p></div>`;
        }

        const response = await fetch(uploadURL, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: sendFormData
        });

        const data = await response.json();
        console.log("FULL BACKEND RESPONSE:", data);

        if (!response.ok) {
            // Invalid token / Session expiry auto-redirect
            if (response.status === 401 || data.detail === "Invalid token") {
                alert("Session expired or invalid token. Please login again.");
                localStorage.removeItem("dhyeya_token");
                window.location.href = "login.html";
                return;
            }
            alert(data.detail || "Upload failed.");
            if (questionList) questionList.innerHTML = "";
            return;
        }

        let rawQuestions = [];
        if (Array.isArray(data)) {
            rawQuestions = data;
        } else if (data.questions && Array.isArray(data.questions)) {
            rawQuestions = data.questions;
        } else if (data.data && Array.isArray(data.data)) {
            rawQuestions = data.data;
        } else {
            rawQuestions = [data];
        }

        if (questionList) {
            questionList.innerHTML = `<h2 style="margin-bottom: 20px; color: #0b3d91;">Detected Document</h2>`;

            if (rawQuestions.length === 0) {
                questionList.innerHTML += `<div class="card" style="padding: 15px;"><p>No content detected.</p></div>`;
                return;
            }

            rawQuestions.forEach((q) => {
                let qText = typeof q === "string" ? q : (q.question_text || q.question || q.text || q.content || "");
                let qAns = typeof q === "object" ? (q.answer || q.ans || "Not generated") : "Not generated";
                let qExp = typeof q === "object" ? (q.explanation || q.exp || "Not available") : "Not available";

                const item = document.createElement("div");
                item.className = "card";
                item.style.marginBottom = "20px";
                item.style.padding = "20px";
                item.style.borderRadius = "8px";
                item.style.backgroundColor = "#ffffff";
                item.style.boxShadow = "0 2px 4px rgba(0,0,0,0.08)";

                const expString = String(qExp);
                const isError = expString.includes("AI Error") || expString.includes("insufficient_quota");
                
                let explanationHTML = "";
                if (isError) {
                    explanationHTML = '<div style="background: #fef2f2; color: #991b1b; padding: 12px; border-radius: 6px; border-left: 4px solid #ef4444; font-size: 14px; margin-top: 5px;">' +
                        '<strong>AI Quota Exhausted:</strong> OpenAI API credits finish ho gaye hain. .env file me key update karein ya Gemini API use karein.' +
                    '</div>';
                } else {
                    explanationHTML = '<div style="background: #f8fafc; color: #334155; padding: 12px; border-radius: 6px; border-left: 4px solid #3b82f6; font-size: 14px; line-height: 1.6; white-space: pre-wrap; margin-top: 5px;">' + qExp + '</div>';
                }

                item.innerHTML = `
                    <div style="font-size: 15px; color: #1e293b; margin-bottom: 15px; line-height: 1.6; white-space: pre-wrap; word-break: break-word;">
                        ${qText}
                    </div>
                    
                    <div style="background: #f0fdf4; color: #166534; padding: 10px 14px; border-radius: 6px; font-weight: 600; margin-bottom: 12px;">
                        Answer: <span style="font-weight: 400;">${qAns}</span>
                    </div>
                    
                    <div>
                        <strong style="color: #475569;">Explanation:</strong>
                        ${explanationHTML}
                    </div>
                `;
                questionList.appendChild(item);
            });
        }

        form.reset();

    } catch (error) {
        console.error("Upload Error Detail:", error);
        alert("Upload Error: " + error.message);
        if (questionList) questionList.innerHTML = "";
    } finally {
        uploadButton.disabled = false;
        uploadButton.innerText = "Upload and Process";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    if (uploadBtn) {
        uploadBtn.addEventListener("click", startUpload);
    }
});