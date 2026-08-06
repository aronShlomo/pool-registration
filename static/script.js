// ================================
// Page Load
// ================================

window.addEventListener("load", async function () {
  if (typeof loadBookedSlots === "function") {
    await loadBookedSlots();
  }

  if (typeof initializeCalendar === "function") {
    initializeCalendar();
  }
});
// ================================
// Stripe Booking
// ================================

const bookButton = document.getElementById("pay_button");

if (bookButton) {
  bookButton.addEventListener("click", async function () {
    bookButton.disabled = true;
    bookButton.innerText = "Processing...";

    const bookingData = {
      name: document.querySelector('input[name="student_name"]').value,

      email: document.querySelector('input[name="email"]').value,

      phone: document.querySelector('input[name="phone"]').value,

      lesson_type: document.querySelector('select[name="lesson_type"]').value,

      package: document.querySelector('select[name="number_lessons"]').value,

      date: document.getElementById("lesson_date").value,

      time: document.getElementById("lesson_time").value,
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

      bookButton.disabled = false;
      bookButton.innerText = "Pay & Reserve Swimming Lesson";

      return;
    }

    try {
      const bookingResponse = await fetch("/create-booking", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(bookingData),
      });

      const bookingResult = await bookingResponse.json();

      console.log("BOOKING RESULT:", bookingResult);

      if (!bookingResponse.ok || !bookingResult.success) {
        alert(bookingResult.error || "Unable to create booking.");

        bookButton.disabled = false;

        bookButton.innerText = "Pay & Reserve Swimming Lesson";

        return;
      }

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

      console.log("STRIPE RESULT:", paymentResult);

      if (paymentResponse.ok && paymentResult.checkout_url) {
        window.location.href = paymentResult.checkout_url;
      } else {
        alert("Stripe Error:\n" + JSON.stringify(paymentResult));

        bookButton.disabled = false;

        bookButton.innerText = "Pay & Reserve Swimming Lesson";
      }
    } catch (error) {
      console.error("PAYMENT ERROR:", error);

      alert("Something went wrong.");

      bookButton.disabled = false;

      bookButton.innerText = "Pay & Reserve Swimming Lesson";
    }
  });
}
