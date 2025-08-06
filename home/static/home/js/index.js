  const hamburger = document.getElementById("hamburger");
  const mobileNav = document.getElementById("mobileNav");

  hamburger.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    mobileNav.classList.toggle("show");
  });



