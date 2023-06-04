const email = document.getElementById("email");
const phone = document.getElementById("phone");
const password = document.getElementById("password");
const repeatPassword = document.getElementById("repeat-password");
const passwordStrength = document.getElementById("password-strength");
const submitButton = document.querySelector('button[type="submit"]');
const form = document.getElementById("form");

// Add event listeners to inputs to validate on change
email.addEventListener("change", validateForm);
phone.addEventListener("change", validateForm);
password.addEventListener("change", validatePassword);
repeatPassword.addEventListener("change", validatePassword);
form.addEventListener("submit", validateForm);

function validateForm() {
  const isValidEmail = email.checkValidity();
  const isValidPhone = phone.checkValidity();
  submitButton.disabled = !(isValidEmail && isValidPhone);
}

function validatePassword() {
  if (password.value !== repeatPassword.value) {
    repeatPassword.setCustomValidity("Passwords do not match");
  } else {
    repeatPassword.setCustomValidity("");

    const strength = calculatePasswordStrength(password.value);
  }
}
function calculatePasswordStrength(password) {
  const weaknesses = {
    length: password.length < 8,
    lowercase: !/[a-z]/.test(password),
    uppercase: !/[A-Z]/.test(password),
    numeric: !/[0-9]/.test(password),
    symbol: !/[!@#$%^&*()]/.test(password),
  };

  const totalWeaknesses = Object.values(weaknesses).filter(Boolean).length;

  switch (totalWeaknesses) {
    case 0:
      setPasswordStrength("strong");
      passwordStrength.style.backgroundColor = "green";
      passwordStrength.style.color = "white";
      break;
    case 1:
      setPasswordStrength("medium");
      passwordStrength.style.backgroundColor = "yellow";
      passwordStrength.style.color = "black";
      break;
    default:
      setPasswordStrength("weak");
      passwordStrength.style.backgroundColor = "red";
      passwordStrength.style.color = "white";
  }

  return weaknesses;
}

function setPasswordStrength(strength) {
  passwordStrength.className = "";
  passwordStrength.classList.add(strength);
  passwordStrength.textContent = `Password strength: ${strength}`;
}

password.addEventListener("input", () => {
  if (password.value.length === 0) {
    setPasswordStrength("");
    return;
  }

  const weaknesses = calculatePasswordStrength(password.value);

  if (weaknesses.length) {
    const passwordStrengthText = Object.keys(weaknesses)
      .filter((key) => weaknesses[key])
      .map((key) => capitalize(key))
      .join(", ");

    password.setCustomValidity(
      `Password is too weak. Weaknesses: ${passwordStrengthText}.`
    );
  } else {
    password.setCustomValidity("");
  }
});

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function showPassword() {
  if (password.type === "password") {
    password.type = "text";
  } else {
    password.type = "password";
  }
}
