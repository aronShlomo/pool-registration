document.addEventListener("DOMContentLoaded", function () {
  // =====================================
  // Search Bookings
  // =====================================

  const searchInput = document.getElementById("searchInput");

  if (searchInput) {
    searchInput.addEventListener("keyup", function () {
      const searchValue = searchInput.value.toLowerCase();

      const rows = document.querySelectorAll("#bookingTable tbody tr");

      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();

        if (text.includes(searchValue)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }

  // =====================================
  // View Booking
  // =====================================

  document.querySelectorAll(".view-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      const bookingId = this.dataset.id;

      try {
        const response = await fetch(`/admin/booking/${bookingId}`);

        const data = await response.json();

        alert(
          `Student: ${data.name}

Email: ${data.email}

Phone: ${data.phone}

Lesson: ${data.lesson_type}

Package: ${data.package}

Date: ${data.lesson_date}

Time: ${data.lesson_time}

Payment: ${data.payment_status}

Status: ${data.status}`,
        );
      } catch (error) {
        console.error(error);

        alert("Unable to load booking details");
      }
    });
  });

  // =====================================
  // Confirm Booking
  // =====================================

  document.querySelectorAll(".confirm-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      updateBookingStatus(this.dataset.id, "confirmed");
    });
  });

  // =====================================
  // Cancel Booking
  // =====================================

  document.querySelectorAll(".cancel-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      updateBookingStatus(this.dataset.id, "cancelled");
    });
  });

  // =====================================
  // Delete Booking
  // =====================================

  document.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      const id = this.dataset.id;

      if (!confirm("Delete this booking?")) {
        return;
      }

      try {
        const response = await fetch(`/admin/delete/${id}`, {
          method: "DELETE",
        });

        const result = await response.json();

        if (result.success) {
          location.reload();
        }
      } catch (error) {
        console.error(error);

        alert("Delete failed");
      }
    });
  });
});

// =====================================
// Update Booking Status
// =====================================

async function updateBookingStatus(id, status) {
  try {
    const response = await fetch(`/admin/update-status/${id}`, {
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
