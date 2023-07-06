const signupForm = document.getElementById("signup-form");
const error = document.getElementById("error");

const phoneNumberInput = document.getElementById("phone");

phoneNumberInput.addEventListener("input", function (event) {
  const inputValue = event.target.value;
  const numericValue = inputValue.replace(/\D/g, "");
  event.target.value = numericValue;
});

function handleSubmit(e) {
  e.preventDefault();

  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const email = document.getElementById("email").value;
  const phone = document.getElementById("phone").value;

  if (!!password && !!confirmPassword && !!email && !!phone) {
    const passwordStrength = zxcvbn(password).score;
    if (password === confirmPassword) {
      if (passwordStrength >= 2) {
        const formData = {
          firstName: firstName,
          lastName: lastName,
          password: password,
          email: email,
          phone: phone,
        };
        // Send the form data to the backend
        fetch("backend-url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        })
          .then((response) => response.json())
          .then((data) => {
            if (response.ok) {
              // Successful login, redirect to the main page
              window.location.href = "../Main/index.html";
            }
          })
          .catch((error) => {
            // Handle any errors that occurred during the request
            console.error(error);
          });
      } else {
        const toast = new bootstrap.Toast(error);
        toast.show();
      }
    } else {
      console.log("test2");
      const errorBody = document.querySelector(".toast-body");
      errorBody.innerText = "Confirm password doesn't match!";
      const toast = new bootstrap.Toast(error);
      toast.show();
    }
  }
}

signupForm.addEventListener("submit", handleSubmit);
