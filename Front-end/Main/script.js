const scrollLinks = document.querySelectorAll(".scroll");

scrollLinks.forEach((link) => {
  link.addEventListener("click", function (e) {
    e.preventDefault();

    const target = document.getElementById(this.getAttribute("data-target"));
    target.scrollIntoView({ behavior: "smooth" });
  });
});