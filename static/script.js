// =====================================
// GLOBAL VARIABLES
// =====================================

let bookedSlots = [];

// =====================================
// PAGE LOAD
// =====================================

window.addEventListener("load", function () {
  initializeCalendar();

  loadBookedSlots();

  updatePrice();
});

// =====================================
// CALENDAR
// =====================================

function initializeCalendar() {
  const calendarElement = document.getElementById("calendar");

  if (!calendarElement) return;

  const calendar = new FullCalendar.Calendar(calendarElement, {
    initialView: "dayGridMonth",

    selectable: true,

    events: "/bookings",

    dateClick: function (info) {
      document.getElementById("lesson_date").value = info.dateStr;

      alert("Selected date: " + info.dateStr);
    },
  });

  calendar.render();
}

// =====================================
// LOAD BOOKED TIMES
// =====================================

async function loadBookedSlots() {
  try {
    const response = await fetch("/booked-slots");

    bookedSlots = await response.json();
  } catch (error) {
    console.error("Booked slots error:", error);
  }
}

// =====================================
// PRICE DISPLAY
// =====================================

function updatePrice() {
  const lesson = document.getElementById("lesson_type");

  const packageSelect = document.getElementById("package");

  const priceBox = document.getElementById("priceDisplay");

  if (!lesson || !packageSelect) return;

  const prices = {
    "Private Lesson": {
      "Single Lesson": 80,

      "4 Lessons Package": 300,

      "8 Lessons Package": 560,

      "Monthly Program": 1000,
    },

    "Semi-Private Lesson": {
      "Single Lesson": 120,

      "4 Lessons Package": 450,

      "8 Lessons Package": 850,

      "Monthly Program": 1500,
    },

    "Group Lesson": {
      "Single Lesson": 60,

      "4 Lessons Package": 220,

      "8 Lessons Package": 400,

      "Monthly Program": 700,
    },
  };

  const value = prices[lesson.value]?.[packageSelect.value];

  if (value) {
    priceBox.innerText = "Price: $" + value;
  } else {
    priceBox.innerText = "Price: Select Lesson";
  }
}

document.getElementById("lesson_type")?.addEventListener("change", updatePrice);

document.getElementById("package")?.addEventListener("change", updatePrice);

// =====================================
// PAYMENT BUTTON
// =====================================

const payButton = document.getElementById("pay_button");

if (payButton) {
  payButton.addEventListener(
    "click",

    async function () {
      payButton.disabled = true;

      payButton.innerText = "Processing...";

      try {
        const bookingData = {
          name: document.querySelector('input[name="name"]').value,

          email: document.querySelector('input[name="email"]').value,

          phone: document.querySelector('input[name="phone"]').value,

          lesson_type: document.querySelector('select[name="lesson_type"]')
            .value,

          package: document.querySelector('select[name="package"]').value,

          date: document.getElementById("lesson_date").value,

          time: document.getElementById("lesson_time").value,
        };

        console.log("BOOKING:", bookingData);

        const bookingResponse = await fetch("/create-booking", {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(bookingData),
        });

        const bookingResult = await bookingResponse.json();

        if (!bookingResponse.ok || !bookingResult.success) {
          alert(bookingResult.error || "Booking failed");

          resetButton();

          return;
        }

        // ================================
        // STRIPE CHECKOUT
        // ================================

        const paymentResponse = await fetch("/create-checkout-session", {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            booking_id: bookingResult.booking_id,
          }),
        });

        const paymentResult = await paymentResponse.json();

        if (!paymentResponse.ok) {
          alert(paymentResult.error);

          resetButton();

          return;
        }

        window.location.href = paymentResult.checkout_url;
        // window.location.href =
        //   "/test-payment-success/" + bookingResult.booking_id;
      } catch (error) {
        console.error(error);

        alert("Something went wrong");

        resetButton();
      }
    },
  );
}

// =====================================
// RESET BUTTON
// =====================================

function resetButton() {
  if (payButton) {
    payButton.disabled = false;

    payButton.innerText = "Pay & Reserve Lesson";
  }
}
