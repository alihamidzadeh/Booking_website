const error = document.getElementById("error");
const loginForm = document.getElementById("login-form");

function handleSubmit(e) {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!!password && !!email) {
    if (email === "test@gmail.com" && password === "testPass") {
      window.location.href = "../Main/index.html";
    } else {
      const toast = new bootstrap.Toast(error);
      toast.show();
    }
  }
}

loginForm.addEventListener("submit", handleSubmit);
