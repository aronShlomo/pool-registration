// ==============================
// LESSON PRICES
// ==============================

const lessonPrices = {
  "Private Lesson": {
    "Single Lesson": "$80",
    "4 Lessons Package": "$300",
    "8 Lessons Package": "$560",
    "Monthly Program": "$650",
  },
  "Semi-Private Lesson": {
    "Single Lesson": "$50",
    "4 Lessons Package": "$180",
    "8 Lessons Package": "$340",
    "Monthly Program": "$400",
  },
  "Group Lesson": {
    "Single Lesson": "$35",
    "4 Lessons Package": "$120",
    "8 Lessons Package": "$220",
    "Monthly Program": "$260",
  },
};

// ==============================
// PRICE DISPLAY
// ==============================

const lessonType = document.getElementById("lesson_type");
const packageType = document.getElementById("package");
const priceDisplay = document.getElementById("priceDisplay");

function getSelectedPrice() {
  const lesson = lessonType?.value;
  const pack = packageType?.value;
  return lessonPrices[lesson]?.[pack] || "";
}

function updatePrice() {
  const price = getSelectedPrice();
  priceDisplay.textContent = price ? `Price: ${price}` : "Price: Select Lesson";
}

lessonType?.addEventListener("change", updatePrice);
packageType?.addEventListener("change", updatePrice);

// ==============================
// GET FORM DATA
// ==============================

function getBookingData() {
  const form = document.getElementById("bookingForm");

  const lessonTypeValue =
    form.lesson_type?.value ||
    document.getElementById("lesson_type")?.value ||
    form.querySelector("[name='lesson_type']")?.value ||
    "";

  const packageValue =
    form.package?.value ||
    document.getElementById("package")?.value ||
    form.querySelector("[name='package']")?.value ||
    "";

  return {
    name: form.name?.value.trim() || "",
    age: form.age?.value || "",
    phone: form.phone?.value.trim() || "",
    email: form.email?.value.trim() || "",
    lesson_type: lessonTypeValue,
    package: packageValue,
    lesson_date: form.date?.value || "",
    lesson_time: form.time?.value || "",
    price: getSelectedPrice(),
    medical: form.medical?.value || "",
    notes: form.notes?.value || "",
  };
}

// ==============================
// MESSAGE
// ==============================

function showMessage(message, success = true) {
  const box = document.getElementById("bookingMessage");
  box.className = success ? "success-message" : "error-message";
  box.innerHTML = message;
}

// ==============================
// SEND FOR APPROVAL
// ==============================

const sendBtn = document.getElementById("sendApprovalBtn");

sendBtn?.addEventListener("click", async () => {
  try {
    const form = document.getElementById("bookingForm");

    const name =
      form.name?.value.trim() ||
      `${form.first_name?.value.trim() || ""} ${form.last_name?.value.trim() || ""}`.trim();

    const ld = form.lesson_date?.value || form.date?.value || "";
    const lt = form.lesson_time?.value || form.time?.value || "";

    const lessonTypeValue =
      form.lesson_type?.value ||
      document.getElementById("lesson_type")?.value ||
      form.querySelector("[name='lesson_type']")?.value ||
      "";

    const packageValue =
      form.package?.value ||
      document.getElementById("package")?.value ||
      form.querySelector("[name='package']")?.value ||
      "";

    const bookingData = {
      name,
      email: form.email?.value.trim() || form.email_address?.value.trim() || "",
      phone: form.phone_number?.value.trim() || form.phone?.value.trim() || "",
      lesson_type: lessonTypeValue,
      package: packageValue,
      lesson_date: ld,
      date: ld,
      lesson_time: lt,
      time: lt,
      price: getSelectedPrice(),
    };

    const response = await fetch("/api/create-booking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData),
    });

    const result = await response.json();

    if (!result.success) {
      showMessage(result.error, false);
      return;
    }

    showMessage("Request sent for approval. The owner will confirm shortly.");
    form.reset();
    updatePrice();
  } catch (err) {
    console.error(err);
    showMessage("Server error. Please try again.", false);
  }
});

// ==============================
// PAY WITH STRIPE
// ==============================

const payBtn = document.getElementById("pay_button");

payBtn?.addEventListener("click", async () => {
  try {
    const bookingData = getBookingData();

    const response = await fetch("/api/create-booking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData),
    });

    const booking = await response.json();

    if (!booking.success) {
      showMessage(booking.error, false);
      return;
    }

    const stripeResponse = await fetch("/api/create-checkout-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ booking_id: booking.booking_id }),
    });

    const stripe = await stripeResponse.json();

    if (stripe.checkout_url) {
      window.location.href = stripe.checkout_url;
    } else {
      showMessage(stripe.error, false);
    }
  } catch (error) {
    console.log(error);
    showMessage("Server error. Please try again.", false);
  }
});

// ==============================
// RESERVE AND PAY LATER
// ==============================

const skipButton = document.getElementById("skip_payment_button");

skipButton?.addEventListener("click", async () => {
  try {
    const bookingData = getBookingData();

    const response = await fetch("/api/create-booking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData),
    });

    const result = await response.json();

    if (!result.success) {
      showMessage(result.error || "Unable to reserve lesson.", false);
      return;
    }

    document.getElementById("bookingMessage").innerHTML = `
      <div class="success-message">
        <h3>✅ Reservation Successful!</h3>
        <p>Your swimming lesson has been reserved.</p>
        <p><b>Payment Method:</b> Pay when you arrive</p>
        <p>We accept:<br>💵 Cash<br>📱 Zelle</p>
        <p>Please complete payment before your lesson begins.</p>
        <p><b>Amount Due:</b> ${bookingData.price}</p>
        <p>Thank you for choosing Millrod Swim Academy!</p>
      </div>
    `;

    document.getElementById("bookingForm").reset();
    updatePrice();
  } catch (error) {
    console.log(error);
    showMessage("Server error. Please try again.", false);
  }
});

// ==============================
// LOAD BOOKED TIMES
// ==============================

async function loadBookedSlots() {
  try {
    const response = await fetch("/api/booked-slots");
    const bookedSlots = await response.json();

    const dateInput = document.getElementById("lesson_date");
    const timeSelect = document.getElementById("lesson_time");

    function updateDisabledTimes() {
      const selectedDate = dateInput.value;

      Array.from(timeSelect.options).forEach((option) => {
        option.disabled = false;
        option.textContent = option.value;
      });

      bookedSlots.forEach((slot) => {
        if (slot.date === selectedDate) {
          Array.from(timeSelect.options).forEach((option) => {
            if (option.value === slot.time) {
              option.disabled = true;
              option.textContent = `${option.value} (Booked)`;
            }
          });
        }
      });
    }

    dateInput.addEventListener("change", updateDisabledTimes);
  } catch (error) {
    console.log("Booked slots error:", error);
  }
}

// ==============================
// AVAILABLE SCHEDULE DISPLAY (FINAL VERSION)
// ==============================

async function loadAvailableSchedule() {
  const scheduleBox = document.getElementById("availableSchedule");
  if (!scheduleBox) return;

  try {
    const response = await fetch("/api/booked-slots");
    const bookedSlots = await response.json();

    const times = [
      "9:00 AM",
      "10:00 AM",
      "11:00 AM",
      "12:00 PM",
      "1:00 PM",
      "2:00 PM",
      "3:00 PM",
      "4:00 PM",
    ];

    const today = new Date();
    let html = "";

    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      if (date.getDay() === 0) continue; // Skip Sunday

      const dbDate = date.toISOString().split("T")[0];
      const displayDate = date.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
      });

      html += `
        <div class="schedule-day">
          <h4>${displayDate}</h4>
          <div class="schedule-times">
      `;

      times.forEach((time) => {
        const booked = bookedSlots.some(
          (slot) => slot.date === dbDate && slot.time === time,
        );

        if (booked) {
          html += `
            <button class="time booked" disabled>
              🔴 ${time}<br>Booked
            </button>
          `;
        } else {
          html += `
            <button class="time available" onclick="selectTime('${dbDate}','${time}')">
              🟢 ${time}
            </button>
          `;
        }
      });

      html += `
          </div>
        </div>
      `;
    }

    scheduleBox.innerHTML = html;
  } catch (error) {
    console.log("Schedule error:", error);
    scheduleBox.innerHTML = "Unable to load schedule.";
  }
}

// ==============================
// SELECT TIME FROM SCHEDULE
// ==============================

function selectTime(date, time) {
  document.getElementById("lesson_date").value = date;
  document.getElementById("lesson_time").value = time;

  document.getElementById("booking").scrollIntoView({ behavior: "smooth" });
}

// ==============================
// INIT
// ==============================

document.addEventListener("DOMContentLoaded", () => {
  loadBookedSlots();
  loadAvailableSchedule();
});
