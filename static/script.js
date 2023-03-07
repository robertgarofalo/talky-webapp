
window.onload=function(){

// Get Buttons
const wordsQuizBtn = document.getElementById('words-btn');
const phrasesQuizBtn = document.getElementById('phrases-btn');
const verbsQuizBtn = document.getElementById('verbs-btn');

// Add links
wordsQuizBtn.addEventListener('click', function(){
      location.href = '/words-quiz';
    });

phrasesQuizBtn.addEventListener('click', function(){
      location.href = '/phrases-quiz';
    });

verbsQuizBtn.addEventListener('click', function(){
      location.href = '/verbs-quiz';
    });

}