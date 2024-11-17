const imageForm = document.getElementById('imageForm');
const detectedImage = document.getElementById('detectedImage');
const resultMessage = document.getElementById('resultMessage');
const downloadButton = document.getElementById('downloadButton');

imageForm.addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Show loading message
    resultMessage.textContent = "Processing image, please wait...";
    
    const formData = new FormData(imageForm);
    
    try {
        const response = await fetch('/detect_image', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            const detectionStatus = jsonResponse.status;

            // Add a cache-busting query parameter to the image URL
            const timestamp = new Date().getTime();
            detectedImage.src = `/static/detected_image.jpg?${timestamp}`;
            detectedImage.style.display = 'block'; // Show the image

            // Show the download button
            downloadButton.href = `/download_image`;
            downloadButton.style.display = 'inline-block';

            // Update result message based on the status
            switch (detectionStatus) {
                case 'uniform_tie_and_shoes_detected':
                    resultMessage.textContent = "School uniform, tie, and shoes detected!";
                    break;
                case 'uniform_tie_no_shoes_detected':
                    resultMessage.textContent = "School uniform and tie detected, but no shoes!";
                    break;
                case 'uniform_tie_detected':
                    resultMessage.textContent = "School uniform and tie detected!";
                    break;
                case 'uniform_and_shoes_detected':
                    resultMessage.textContent = "School uniform and shoes detected!";
                    break;
                case 'uniform_no_shoes_detected':
                    resultMessage.textContent = "School uniform detected, but no shoes!";
                    break;
                case 'uniform_detected':
                    resultMessage.textContent = "School uniform detected!";
                    break;
                case 'non_uniform_tie_and_shoes_detected':
                    resultMessage.textContent = "Non-school uniform, tie, and shoes detected!";
                    break;
                case 'non_uniform_tie_no_shoes_detected':
                    resultMessage.textContent = "Non-school uniform and tie detected, but no shoes!";
                    break;
                case 'non_uniform_tie_detected':
                    resultMessage.textContent = "Non-school uniform and tie detected!";
                    break;
                case 'non_uniform_and_shoes_detected':
                    resultMessage.textContent = "Non-school uniform and shoes detected!";
                    break;
                case 'non_uniform_no_shoes_detected':
                    resultMessage.textContent = "Non-school uniform detected, but no shoes!";
                    break;
                case 'non_uniform_detected':
                    resultMessage.textContent = "Non-school uniform detected!";
                    break;
                case 'tie_and_shoes_detected':
                    resultMessage.textContent = "Tie and shoes detected!";
                    break;
                case 'tie_no_shoes_detected':
                    resultMessage.textContent = "Tie detected, but no shoes!";
                    break;
                case 'tie_detected':
                    resultMessage.textContent = "Tie detected!";
                    break;
                case 'shoes_detected':
                    resultMessage.textContent = "Shoes detected!";
                    break;
                case 'no_shoes_detected':
                    resultMessage.textContent = "No shoes detected!";
                    break;
                case 'no_detection':
                    resultMessage.textContent = "No detection made!";
                    break;
                default:
                    resultMessage.textContent = "Unexpected status returned.";
            }
            
    }} catch (error) {
        console.error(error); // Log the error to the console for debugging
        resultMessage.textContent = "Image detection failed. Please try again.";
        downloadButton.style.display = 'none'; // Hide download button on failure
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Create an intersection observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    // Select all elements with the animated class
    const elements = document.querySelectorAll('.animated');
    elements.forEach(el => {
        observer.observe(el);
    });
});

const confidenceSlider = document.getElementById('confidence');
const confidenceValueDisplay = document.getElementById('confidenceValue');

confidenceSlider.oninput = function() {
    confidenceValueDisplay.textContent = this.value;
};
