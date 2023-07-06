const error = document.getElementById("error");
const loginForm = document.getElementById("login-form");

function handleSubmit(e) {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!!password && !!email) {
    fetch("backend-url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: email, password: password }),
    })
      .then((response) => {
        if (response.ok) {
          // Successful login, redirect to the main page
          window.location.href = "../Main/index.html";
        } else {
          const toast = new bootstrap.Toast(error);
          toast.show();
        }
      })
      .catch((error) => {
        // Handle network or server errors
        console.error(error);
      });
  }
}

loginForm.addEventListener("submit", handleSubmit);
