// ================================
// Page Load
// ================================

window.addEventListener("load", async function () {
  await loadBookedSlots();
  initializeCalendar();
});

// ================================
// Stripe Booking
// ================================

const bookButton = document.getElementById("bookLessonBtn");

if (bookButton) {
  bookButton.addEventListener("click", async function () {
    bookButton.disabled = true;
    bookButton.innerText = "Processing...";

    const bookingData = {
      name:
        document.querySelector('input[name="first_name"]').value +
        " " +
        document.querySelector('input[name="last_name"]').value,

      email: document.querySelector('input[name="email"]').value,

      phone: document.querySelector('input[name="phone_number"]').value,

      lesson_type: document.getElementById("lesson_type").value,

      package: document.getElementById("package").value,

      date: document.getElementById("lesson_date").value,

      time: document.getElementById("lesson_time").value,
    };

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
      bookButton.innerText = "Pay & Book Lesson";

      return;
    }

    try {
      // Create booking
      const bookingResponse = await fetch("/create-booking", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(bookingData),
      });

      const bookingResult = await bookingResponse.json();

      if (!bookingResponse.ok || !bookingResult.success) {
        alert(bookingResult.error || "Unable to create booking.");

        bookButton.disabled = false;
        bookButton.innerText = "Pay & Book Lesson";

        return;
      }

      // Create Stripe Checkout
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

      if (paymentResponse.ok && paymentResult.checkout_url) {
        window.location.href = paymentResult.checkout_url;
      } else {
        alert(paymentResult.error || "Unable to start Stripe checkout.");

        bookButton.disabled = false;
        bookButton.innerText = "Pay & Book Lesson";
      }
    } catch (error) {
      console.error(error);

      alert("An unexpected error occurred.");

      bookButton.disabled = false;
      bookButton.innerText = "Pay & Book Lesson";
    }
  });
}
