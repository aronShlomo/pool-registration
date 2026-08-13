document.addEventListener("DOMContentLoaded", function () {
  // =====================================
  // SEARCH BOOKINGS
  // =====================================

  const searchInput = document.getElementById("searchInput");

  if (searchInput) {
    searchInput.addEventListener("keyup", function () {
      const value = searchInput.value.toLowerCase();

      document
        .querySelectorAll("#bookingTable tbody tr")
        .forEach(function (row) {
          const text = row.textContent.toLowerCase();

          if (text.includes(value)) {
            row.style.display = "";
          } else {
            row.style.display = "none";
          }
        });
    });
  }

  // =====================================
  // VIEW BOOKING
  // =====================================

  document.querySelectorAll(".view-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      const id = this.dataset.id;

      try {
        const response = await fetch(`/api/admin/booking/${id}`);

        const booking = await response.json();

        alert(
          `
Student:
${booking.name}


Email:
${booking.email}


Phone:
${booking.phone}


Lesson:
${booking.lesson_type}


Package:
${booking.package}


Date:
${booking.lesson_date}


Time:
${booking.lesson_time}


Payment:
${booking.payment_status}


Status:
${booking.status}

`,
        );
      } catch (error) {
        console.error(error);

        alert("Unable to load booking");
      }
    });
  });

  // =====================================
  // CONFIRM BOOKING
  // =====================================

  document.querySelectorAll(".confirm-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.dataset.id;

      if (confirm("Confirm this booking?")) {
        updateBookingStatus(id, "confirmed");
      }
    });
  });

  // =====================================
  // CANCEL BOOKING
  // =====================================

  document.querySelectorAll(".cancel-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.dataset.id;

      if (confirm("Cancel this booking?")) {
        updateBookingStatus(id, "cancelled");
      }
    });
  });
});

// =====================================
// UPDATE STATUS
// =====================================

async function updateBookingStatus(id, status) {
  try {
    const response = await fetch(`/api/admin/update-status/${id}`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        status: status,
      }),
    });

    const result = await response.json();

    if (result.success) {
      location.reload();
    } else {
      alert(result.error || "Update failed");
    }
  } catch (error) {
    console.error(error);

    alert("Server error");
  }
}
