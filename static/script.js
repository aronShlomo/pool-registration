// ================================
// Load booked lesson times
// ================================

let bookedSlots = [];

async function loadBookedSlots() {
  try {
    const response = await fetch("/booked-slots");

    if (!response.ok) {
      throw new Error("Failed to load booked slots.");
    }

    bookedSlots = await response.json();
  } catch (error) {
    console.error("Error loading booked slots:", error);
  }
}

// ================================
// Disable booked time slots
// ================================

const dateInput = document.getElementById("lesson_date");
const timeSelect = document.getElementById("lesson_time");

if (dateInput && timeSelect) {
  dateInput.addEventListener("change", async () => {
    await loadBookedSlots();

    const selectedDate = dateInput.value;

    [...timeSelect.options].forEach((option) => {
      if (option.value === "") return;

      option.disabled = false;
      option.text = option.value;

      const booked = bookedSlots.some(
        (slot) => slot.date === selectedDate && slot.time === option.value,
      );

      if (booked) {
        option.disabled = true;
        option.text = option.value + " (Booked)";
      }
    });
  });
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

    // Always reload latest bookings
    await loadBookedSlots();

    const lessonDate = formData.get("lesson_date");
    const lessonTime = formData.get("lesson_time");

    const alreadyBooked = bookedSlots.some(
      (slot) => slot.date === lessonDate && slot.time === lessonTime,
    );

    if (alreadyBooked) {
      message.style.color = "red";

      message.innerHTML =
        "❌ This appointment has already been booked. Please choose another date or time.";

      return;
    }

    try {
      const response = await fetch("/register", {
        method: "POST",

        body: formData,
      });

      const data = await response.json();

      console.log(data);

      if (data.success) {
        message.style.color = "green";

        message.innerHTML = data.message;

        form.reset();

        await loadBookedSlots();

        if (window.calendar) {
          window.calendar.refetchEvents();
        }
      } else {
        message.style.color = "red";

        message.innerHTML = data.message;

        await loadBookedSlots();
      }
    } catch (error) {
      console.error(error);

      message.style.color = "red";

      message.innerHTML = "Server error. Please try again later.";
    }
  });
}

// ================================
// Initial page load
// ================================

window.addEventListener("load", async () => {
  await loadBookedSlots();
});
