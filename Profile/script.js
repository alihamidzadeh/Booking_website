var saveEl = document.getElementById("save-btn");
const firstName = document.getElementById("firstName").value;
const lastName = document.getElementById("lastName").value;
const email = document.getElementById("email").value;
const address = document.getElementById("address").value;
const phone = document.getElementById("phone").value;
const birthdate = document.getElementById("birthdate").value;
const saveChangesButton = document.getElementById("saveChanges").value;

function upload() {
  var input = document.querySelector("input[type=file]");
  var reader = new FileReader();

  reader.onloadend = function () {
    var avatar = document.querySelector(".avatar");
    avatar.src = reader.result;
  };

  reader.readAsDataURL(input.files[0]);
}

document.getElementById("phone").addEventListener("input", function (e) {
  this.value = this.value.replace(/[^0-9]/g, "");
});

function saveProfileEdit() {
  var saveEl = document.getElementById("save-btn");
  saveEl.className = "saved";
  document.getElementById("save-btn").innerHTML = "SAVED ✓";
}

saveChangesButton.addEventListener("click", () => {
  const payload = {
    firstName: firstName,
    lastName: lastName,
    email: email,
    address: address,
    phone: phone,
    birthdate: birthdate,
  };

  // Send the HTTP request to the backend
  fetch("backend-url", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => {
      // Handle the response from the server
      console.log("Profile updated successfully:", data);
      // Perform any necessary actions after successful update
    })
    .catch((error) => {
      console.error("Error updating profile:", error);
      // Handle the error accordingly
    });
});
