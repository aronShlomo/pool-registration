// ================================
// Global Variables
// ================================

let bookedSlots = [];
let calendar;

// ================================
// Load booked lesson times
// ================================

async function loadBookedSlots() {
  try {
    const response = await fetch("/booked-slots");

    if (!response.ok) {
      throw new Error("Failed to load booked slots");
    }

    bookedSlots = await response.json();
  } catch (error) {
    console.error("Loading bookings error:", error);
  }
}

// ================================
// FullCalendar Setup
// ================================

function initializeCalendar() {
  const calendarElement = document.getElementById("calendar");

  if (!calendarElement) {
    return;
  }

  if (typeof FullCalendar === "undefined") {
    console.error("FullCalendar failed to load");
    return;
  }

  calendar = new FullCalendar.Calendar(calendarElement, {
    initialView: "dayGridMonth",

    selectable: true,

    events: "/bookings",

    eventColor: "#d9534f",

    eventClick: function (info) {
      alert("Booked lesson:\n" + info.event.title);
    },

    dateClick: function (info) {
      const dateInput = document.getElementById("lesson_date");

      if (dateInput) {
        dateInput.value = info.dateStr;

        dateInput.dispatchEvent(new Event("change"));
      }
    },
  });

  calendar.render();

  window.calendar = calendar;
}

// ================================
// Disable booked times
// ================================

const dateInput = document.getElementById("lesson_date");
const timeSelect = document.getElementById("lesson_time");

if (dateInput && timeSelect) {
  dateInput.addEventListener("change", async function () {
    await loadBookedSlots();

    const selectedDate = dateInput.value;

    [...timeSelect.options].forEach((option) => {
      if (option.value === "") {
        return;
      }

      // RESET EVERY TIME USER CHANGES DATE
      option.disabled = false;

      option.textContent = option.value;

      const booked = bookedSlots.some(
        (slot) => slot.date === selectedDate && slot.time === option.value,
      );

      if (booked) {
        option.disabled = true;

        option.textContent = option.value + " (Booked)";
      }
    });
  });
}

// ================================
// Prevent past dates
// ================================

if (dateInput) {
  const today = new Date().toISOString().split("T")[0];

  dateInput.min = today;
}

// ================================
// Booking Form
// ================================

const form = document.getElementById("bookingForm");

if (form) {
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const message = document.getElementById("bookingMessage");

    message.style.color = "black";

    message.innerHTML = "Submitting registration...";

    const formData = new FormData(form);

    await loadBookedSlots();

    const alreadyBooked = bookedSlots.some(
      (slot) =>
        slot.date === formData.get("lesson_date") &&
        slot.time === formData.get("lesson_time"),
    );

    if (alreadyBooked) {
      message.style.color = "red";

      message.innerHTML =
        "❌ This appointment is already booked. Please choose another time.";

      return;
    }

    try {
      const response = await fetch("/register", {
        method: "POST",

        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        message.style.color = "green";

        message.innerHTML = "✅ " + data.message;

        form.reset();

        if (dateInput) {
          dateInput.dispatchEvent(new Event("change"));
        }

        await loadBookedSlots();

        // Refresh the time dropdown after booking
        if (dateInput) {
          dateInput.dispatchEvent(new Event("change"));
        }

        if (calendar) {
          calendar.refetchEvents();
        }
      } else {
        message.style.color = "red";

        message.innerHTML = data.message;
      }
    } catch (error) {
      console.error(error);

      message.style.color = "red";

      message.innerHTML = "Server error. Please try again.";
    }
  });
}

// ================================
// Page Load
// ================================

window.addEventListener("load", async function () {
  await loadBookedSlots();

  initializeCalendar();
});
