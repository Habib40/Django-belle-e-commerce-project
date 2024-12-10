document.addEventListener('DOMContentLoaded', function () {
    // Adjust the selector to target the right dropdown
    const colorSelect = document.querySelector('#id_color'); // Ensure this matches your select's id
    const savedColorName = document.querySelector('input[name="name"]').value; // Adjust if needed

    if (colorSelect) {
        const options = colorSelect.querySelectorAll('option');
        options.forEach(option => {
            if (option.value === savedColorName) {
                option.style.backgroundColor = 'yellow'; // Highlight color
                option.style.color = 'black'; // Adjust text color
            }
        });
    } else {
        console.error('Color select element not found.');
    }
});