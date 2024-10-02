// Function to show the quiz menu when "Start Quiz" is clicked
function showQuizMenu() {
    const quizMenu = document.getElementById('quiz-menu');
    quizMenu.classList.remove('hidden');
}

// Function to start the selected quiz
function startSelectedQuiz() {
    const selectedQuiz = document.getElementById('quiz-select').value;
    if (selectedQuiz) {
        alert(`Starting the ${selectedQuiz} quiz!`);
    } else {
        alert("Please select a quiz subject.");
    }
}

// Function for showing results (currently a placeholder)
function showResults() {
    alert("Displaying quiz results (Feature coming soon).");
}

// Function for tracking progress (currently a placeholder)
function trackProgress() {
    alert("Displaying progress (Feature coming soon).");
}
