// =====================================
// PAGE LOAD
// =====================================

window.addEventListener("load", function () {
  if (typeof initializeCalendar === "function") {
    initializeCalendar();
  }

  if (typeof loadBookedSlots === "function") {
    loadBookedSlots();
  }
});

// =====================================
// STRIPE BOOKING
// =====================================

const payButton = document.getElementById("pay_button");

if (payButton) {
  payButton.addEventListener("click", async function () {
    payButton.disabled = true;

    payButton.innerText = "Processing...";

    try {
      const bookingData = {
        name: document.querySelector('input[name="student_name"]').value,

        email: document.querySelector('input[name="email"]').value,

        phone: document.querySelector('input[name="phone"]').value,

        lesson_type: document.querySelector('select[name="lesson_type"]').value,

        package: document.querySelector('select[name="package"]').value,

        date: document.getElementById("lesson_date").value,

        time: document.getElementById("lesson_time").value,

        medical: document.querySelector('textarea[name="medical"]').value,

        notes: document.querySelector('textarea[name="notes"]').value,
      };

      console.log("BOOKING DATA:", bookingData);

      if (
        !bookingData.name ||
        !bookingData.email ||
        !bookingData.lesson_type ||
        !bookingData.package ||
        !bookingData.date ||
        !bookingData.time
      ) {
        alert("Please complete all required booking information.");

        resetButton();

        return;
      }

      // =============================
      // CREATE BOOKING
      // =============================

      const bookingResponse = await fetch("/create-booking", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(bookingData),
      });

      const bookingResult = await bookingResponse.json();

      console.log("BOOKING RESPONSE:", bookingResult);

      if (!bookingResponse.ok || !bookingResult.success) {
        alert(bookingResult.error || "Booking failed");

        resetButton();

        return;
      }

      // =============================
      // STRIPE CHECKOUT
      // =============================

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

      console.log("STRIPE RESPONSE:", paymentResult);

      if (paymentResponse.ok && paymentResult.checkout_url) {
        window.location.href = paymentResult.checkout_url;
      } else {
        alert("Stripe Error: " + JSON.stringify(paymentResult));

        resetButton();
      }
    } catch (error) {
      console.error("ERROR:", error);

      alert("Something went wrong. Please try again.");

      resetButton();
    }
  });
}

// =====================================
// RESET BUTTON
// =====================================

function resetButton() {
  if (payButton) {
    payButton.disabled = false;

    payButton.innerText = "Pay & Reserve Swimming Lesson";
  }
}
