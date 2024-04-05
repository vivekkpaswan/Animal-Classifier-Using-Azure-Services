// script.js
const form = document.getElementById('uploadForm');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/classify', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        displayResult(file, data.animal);
    } catch (error) {
        console.error('Error:', error);
    }
});

function displayResult(file, animal) {
    const resultDiv = document.getElementById('result');

    // Create container for uploaded image and predicted name
    const animalContainer = document.createElement('div');
    animalContainer.classList.add('animal');

    // Display the uploaded image
    const uploadedImage = document.createElement('img');
    uploadedImage.src = URL.createObjectURL(file);
    uploadedImage.alt = 'Uploaded Animal';
    uploadedImage.style.width = '200px'; // Fixed width
    uploadedImage.style.height = '200px'; // Fixed height
    uploadedImage.style.border = '1px solid #ccc';
    uploadedImage.style.borderRadius = '5px';
    animalContainer.appendChild(uploadedImage);

    // Display the predicted name
    const animalName = document.createElement('p');
    animalName.textContent = animal;
    animalName.classList.add('predicted-name');
    animalContainer.appendChild(animalName);

    // Append the container to the result div
    resultDiv.appendChild(animalContainer);
}

// Popup script
const openPopupBtn = document.getElementById('openPopupBtn');
const closePopupBtn = document.getElementById('closePopupBtn');
const popup = document.getElementById('popup');
const overlay = document.getElementById('overlay');
const translationResult = document.getElementById('translationResult');

openPopupBtn.addEventListener('click', () => {
    popup.style.display = 'block';
    overlay.style.display = 'block';
});

closePopupBtn.addEventListener('click', () => {
    popup.style.display = 'none';
    overlay.style.display = 'none';
});

overlay.addEventListener('click', () => {
    popup.style.display = 'none';
    overlay.style.display = 'none';
});

document.getElementById('translateBtn').addEventListener('click', () => {
    const text = document.getElementById('text').value;
    const targetLanguage = document.getElementById('target_language').value;
    const url = '/translate';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text,
            target_language: targetLanguage
        })
    })
    .then(response => response.json())
    .then(result => {
        translationResult.innerHTML = result.translation;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});