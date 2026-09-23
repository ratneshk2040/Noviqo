const practiceApiBase = "/api/practice";

let currentQuiz = [];


// Authentication

function getToken() {

    const token = localStorage.getItem("dhyeya_token");

    if (!token) {
        location.href = "login.html";
        return null;
    }

    return token;
}



// Common API Function

async function apiRequest(url, options = {}) {

    const response = await fetch(
        `${practiceApiBase}${url}`,
        options
    );


    let data;

    try {
        data = await response.json();
    }
    catch {
        throw new Error("Invalid server response");
    }


    if (!response.ok) {
        throw new Error(
            data.detail || "Request failed"
        );
    }


    return data;
}



// Generate Quiz

async function loadQuiz(event) {

    event.preventDefault();


    const token = getToken();

    if (!token) return;



    const form =
        document.getElementById("quizForm");


    const button =
        form.querySelector("button");


    const container =
        document.getElementById("quizContainer");



    const quizData = {

        subject:
        form.subject.value.trim() || null,


        topic:
        form.topic.value.trim() || null,


        count:
        Number(form.count.value) || 5

    };



    try {

        button.disabled = true;

        button.innerText =
        "Generating...";



        container.innerHTML = `
            <div class="card">
                <p>Generating questions...</p>
            </div>
        `;



        const data = await apiRequest(
            "/quiz",
            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json",

                    Authorization:
                    `Bearer ${token}`

                },

                body:
                JSON.stringify(quizData)

            }
        );



        currentQuiz =
        data.questions || data;



        if(
            !Array.isArray(currentQuiz) ||
            currentQuiz.length === 0
        ){

            container.innerHTML = `
                <div class="card">
                    <p>No questions found.</p>
                </div>
            `;

            return;
        }



        displayQuiz(currentQuiz);


        document.getElementById(
            "submitQuizBtn"
        ).style.display="block";



    }


    catch(error){

        console.error(
            "Quiz Error:",
            error
        );

        alert(error.message);


    }


    finally{

        button.disabled=false;

        button.innerText =
        "Create Quiz";

    }

}



// Display Quiz

function displayQuiz(items){


    const container =
    document.getElementById(
        "quizContainer"
    );



    container.innerHTML =
    items.map((q,index)=>{


        const options =
        (q.options || [])
        .map(opt=>`

            <label class="option">

                <input 
                type="radio"
                name="q_${q.question_id}"
                value="${opt.label}">

                ${opt.label}. ${opt.text}

            </label>

        `)
        .join("");



        return `

        <div class="card">

            <h3>
                Question ${index+1}
            </h3>


            <p>
                ${q.question_text}
            </p>


            <div>
                ${options}
            </div>


        </div>

        `;


    }).join("");



    document.getElementById(
        "quizResults"
    ).innerHTML="";

}



// Submit Quiz

async function submitQuiz(){


    const token = getToken();

    if(!token) return;



    if(currentQuiz.length===0){

        alert(
            "Generate quiz first."
        );

        return;

    }



    let correct = 0;



    const answers =
    currentQuiz.map(q=>{


        const selected =
        document.querySelector(
            `input[name="q_${q.question_id}"]:checked`
        );



        const answer =
        selected ?
        selected.value :
        null;



        const status =
        answer === q.correct_option;



        if(status)
            correct++;



        return {

            question_id:
            q.question_id,


            selected_option:
            answer,


            correct:
            status

        };


    });



    const total =
    currentQuiz.length;



    try{


        const data =
        await apiRequest(
            "/session",
            {

                method:"POST",

                headers:{

                    "Content-Type":
                    "application/json",

                    Authorization:
                    `Bearer ${token}`

                },


                body:
                JSON.stringify({

                    upload_id:null,

                    score:correct,

                    total_questions:total,

                    correct_count:correct,

                    wrong_count:
                    total-correct,

                    answers:answers

                })

            }
        );



        showResult(
            correct,
            total-correct,
            total
        );


    }


    catch(error){

        console.error(error);

        alert(error.message);

    }

}



// Result

function showResult(correct,wrong,total){


    document.getElementById(
        "quizResults"
    ).innerHTML = `

    <div class="card">

        <h3>
            Quiz Result
        </h3>


        <p>
            Score: ${correct}/${total}
        </p>


        <p>
            Correct: ${correct}
        </p>


        <p>
            Wrong: ${wrong}
        </p>


    </div>

    `;

}



// Connect Page

document.addEventListener(
"DOMContentLoaded",
()=>{


    const quizForm =
    document.getElementById(
        "quizForm"
    );


    if(quizForm){

        quizForm.addEventListener(
            "submit",
            loadQuiz
        );

    }



    const submitBtn =
    document.getElementById(
        "submitQuizBtn"
    );


    if(submitBtn){

        submitBtn.onclick =
        submitQuiz;

    }


});