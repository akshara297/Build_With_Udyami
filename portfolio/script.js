const menuButton = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav-links");

// Mobile navigation
if (menuButton && navLinks) {
  menuButton.addEventListener("click", () => {
    const isOpen = menuButton.getAttribute("aria-expanded") === "true";

    menuButton.setAttribute("aria-expanded", String(!isOpen));
    menuButton.setAttribute(
      "aria-label",
      isOpen ? "Open navigation" : "Close navigation"
    );
    navLinks.classList.toggle("open", !isOpen);
  });

  navLinks.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.setAttribute("aria-label", "Open navigation");
    });
  });
}

// Expand/collapse project stories
document.querySelectorAll(".details-toggle").forEach(button => {
  button.addEventListener("click", () => {
    const detailsId = button.getAttribute("aria-controls");
    const details = document.getElementById(detailsId);

    if (!details) return;

    const isExpanded = button.getAttribute("aria-expanded") === "true";

    button.setAttribute("aria-expanded", String(!isExpanded));
    details.hidden = isExpanded;

    const label = isExpanded
      ? button.textContent.includes("idea")
        ? "Behind the idea"
        : "Behind the build"
      : "Close story";

    const icon = isExpanded ? "↗" : "×";
    button.innerHTML = `${label} <span class="toggle-icon">${icon}</span>`;
  });
});

// Reveal sections as they enter the viewport
const revealItems = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver((entries, currentObserver) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        currentObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12
  });

  revealItems.forEach(item => observer.observe(item));
} else {
  revealItems.forEach(item => item.classList.add("is-visible"));
}

// Copy email address
const copyButton = document.getElementById("copy-email");
const copyFeedback = document.getElementById("copy-feedback");

if (copyButton && copyFeedback) {
  copyButton.addEventListener("click", async () => {
    const email = copyButton.dataset.email;

    try {
      await navigator.clipboard.writeText(email);
      copyFeedback.textContent = "Email copied! See you in the inbox ✿";
    } catch {
      copyFeedback.textContent = `Email: ${email}`;
    }
  });
}