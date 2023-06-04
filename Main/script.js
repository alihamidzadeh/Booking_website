const scrollLinks = document.querySelectorAll(".scroll");
const scrollUpBtn = document.querySelector("#scroll-up-btn");

scrollLinks.forEach((link) => {
  link.addEventListener("click", function (e) {
    e.preventDefault();

    const target = document.getElementById(this.getAttribute("data-target"));
    target.scrollIntoView({ behavior: "smooth" });
  });
});

window.addEventListener("scroll", () => {
  if (window.pageYOffset > 200) {
    scrollUpBtn.classList.add("visible");
  } else {
    scrollUpBtn.classList.remove("visible");
  }
});

scrollUpBtn.addEventListener("click", () => {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
});

function googleTranslateElementInit() {
  new google.translate.TranslateElement(
    { pageLanguage: "en" },
    "google_translate_element"
  );
}
