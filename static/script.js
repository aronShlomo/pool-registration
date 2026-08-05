const form = document.getElementById("bookingForm");

if (form) {
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const message = document.getElementById("bookingMessage");

    message.innerHTML = "Submitting registration...";

    const formData = new FormData(form);

    try {
      const response = await fetch("/register", {
        method: "POST",

        body: formData,
      });

      const data = await response.json();

      console.log(data);

      message.innerHTML = data.message;

      if (data.success) {
        message.style.color = "green";

        form.reset();

        if (window.calendar) {
          calendar.refetchEvents();
        }
      } else {
        message.style.color = "red";
      }
    } catch (error) {
      console.error(error);

      message.innerHTML = "Server error. Check Flask console.";

      message.style.color = "red";
    }
  });
}
