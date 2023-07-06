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

  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const email = document.getElementById("email").value;
  const phone = document.getElementById("phone").value;

  if (!!password && !!confirmPassword && !!email && !!phone) {
    const passwordStrength = zxcvbn(password).score;
    if (password === confirmPassword) {
      if (passwordStrength >= 2) {
        alert("success");
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
