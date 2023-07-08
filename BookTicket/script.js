// Get the dropdown menu
var dropdownMenu = document.querySelector(".dropdown-menu");

// Get all the dropdown items
var dropdownItems = dropdownMenu.querySelectorAll(".dropdown-item");

// Add click event listener to each dropdown item
dropdownItems.forEach(function (item) {
  item.addEventListener("click", function (e) {
    e.preventDefault();

    var selectedGender = this.text;
    var button = document.getElementById("genderDropdown");
    button.innerText = selectedGender;
    console.log("Selected Gender:", selectedGender);
  });
});

document.getElementById("nationalID").addEventListener("input", function (e) {
  this.value = this.value.replace(/[^0-9]/g, "");
});
