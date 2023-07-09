var formData = {
  from: document.getElementById("from").value,
  to: document.getElementById("to").value,
  departure: document.getElementById("departure").value,
  return: document.getElementById("return").value,
  passengers: document.getElementById("passengers").value,
};

document
  .getElementById("flightForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    fetch("/your-backend-url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
      });
  });
