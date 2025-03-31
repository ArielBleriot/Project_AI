$(document).ready(function(){
    // Handle login form submission
    $('#loginFormSubmit').submit(function(e){
        e.preventDefault();  // Prevent the default form submission

        // Prepare data for the request
        let username = $('#loginUsername').val();
        let password = $('#loginPassword').val();

        // Create a JSON object with the form data
        let data = {
            username: username,
            password: password
        };

        // Make the AJAX request
        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json', // Explicitly set the content type as JSON
            data: JSON.stringify(data),  // Convert the data object to a JSON string
            success: function(response){
                // Handle success response
                if (response.success) {
                    window.location.href = '/chat'; // Redirect to the home page
                } else {
                    alert(response.message);  // Show error message
                }
            },
            error: function(){
                alert('Login failed. Please try again.');  // Handle unexpected errors
            }
        });
    });
});
