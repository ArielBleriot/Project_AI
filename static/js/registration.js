document.addEventListener("DOMContentLoaded", function () {
    // Show registration form when clicking "Show Register"
    document.getElementById('showRegister').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector('.signin > .content').style.display = 'none'; // Hide login form
        document.getElementById('registerForm').style.display = 'block'; // Show registration form
    });

    // Handle registration form submission
    document.getElementById('registerFormSubmit').addEventListener('submit', async function (e) {
        e.preventDefault();  // Prevent the form from submitting the normal way

        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;
        const email = document.getElementById('registerEmail').value;

        const data = JSON.stringify({ username, password, email });

        console.log("Sending data:", data);  // Debugging

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: data
            });

            const result = await response.json();

            if (result.success) {
                alert('User registered successfully!');

                // Hide the registration form and show the login form
                document.getElementById('registerForm').style.display = 'none';
                document.querySelector('.signin > .content').style.display = 'block';

                // Clear the form
                document.getElementById('registerFormSubmit').reset();
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});
