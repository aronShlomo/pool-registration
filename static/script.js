document.addEventListener("DOMContentLoaded", function () {
  // =========================
  // FULL CALENDAR
  // =========================

  let calendarElement = document.getElementById("calendar");

  if (calendarElement) {
    window.calendar = new FullCalendar.Calendar(calendarElement, {
      initialView: "dayGridMonth",

      selectable: true,

      events: "/bookings",

      dateClick: function (info) {
        document.getElementById("lesson_date").value = info.dateStr;

        document.getElementById("bookingForm").scrollIntoView({
          behavior: "smooth",
        });
      },
    });

    calendar.render();
  }

  // =========================
  // BOOKING FORM SUBMIT
  // =========================

  const form = document.getElementById("bookingForm");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      let formData = new FormData(form);

      fetch("/register", {
        method: "POST",

        body: formData,
      })
        .then((response) => response.json())

        .then((data) => {
          let message = document.getElementById("bookingMessage");

          message.innerHTML = data.message;

          if (data.success) {
            message.style.color = "green";

            form.reset();

            if (window.calendar) {
              window.calendar.refetchEvents();
            }
          } else {
            message.style.color = "red";
          }
        })

        .catch((error) => {
          console.error("Error:", error);
        });
    });
  }
});
