document.addEventListener('DOMContentLoaded', function () {
    // Get the saved color name from the input field
    const savedColorName = document.querySelector('.field-name input').value;
    
    // Find the dropdown options
    const colorOptions = document.querySelectorAll('.field-name select option');

    // Highlight the matching color option
    colorOptions.forEach(option => {
        if (option.value === savedColorName) {
            option.style.backgroundColor = 'yellow'; // Highlight color
            option.style.color = 'black'; // Adjust text color for better readability
        }
    });
});