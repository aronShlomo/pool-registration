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
  const lesson = lessonType.value;
  const pack = packageType.value;

  if (lessonPrices[lesson] && lessonPrices[lesson][pack]) {
    return lessonPrices[lesson][pack];
  }

  return "";
}

function updatePrice() {
  const price = getSelectedPrice();

  if (price) {
    priceDisplay.textContent = "Price: " + price;
  } else {
    priceDisplay.textContent = "Price: Select Lesson";
  }
}

lessonType.addEventListener("change", updatePrice);

packageType.addEventListener("change", updatePrice);

// ==============================
// GET FORM DATA
// ==============================

function getBookingData() {
  const form = document.getElementById("bookingForm");

  return {
    name: form.name.value.trim(),

    age: form.age.value,

    phone: form.phone.value.trim(),

    email: form.email.value.trim(),

    lesson_type: form.lesson_type.value,

    package: form.package.value,

    lesson_date: form.date.value,

    lesson_time: form.time.value,

    price: getSelectedPrice(),

    medical: form.medical.value,

    notes: form.notes.value,
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
// PAY WITH STRIPE
// ==============================

document.getElementById("pay_button").addEventListener("click", async () => {
  try {
    const bookingData = getBookingData();

    const response = await fetch("/create-booking", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(bookingData),
    });

    const booking = await response.json();

    if (!booking.success) {
      showMessage(booking.error, false);

      return;
    }

    const stripeResponse = await fetch("/create-checkout-session", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        booking_id: booking.booking_id,
      }),
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

if (skipButton) {
  skipButton.addEventListener("click", async () => {
    try {
      const bookingData = getBookingData();

      const response = await fetch("/create-booking", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(bookingData),
      });

      const result = await response.json();

      if (result.success) {
        document.getElementById("bookingMessage").innerHTML = `


<div class="success-message">


<h3>
✅ Reservation Successful!
</h3>



<p>
Your swimming lesson has been reserved.
</p>



<p>
<b>
Payment Method:
</b>
Pay when you arrive
</p>



<p>
We accept:
<br>
💵 Cash
<br>
📱 Zelle
</p>



<p>
Please complete payment before your lesson begins.
</p>



<p>
<b>
Amount Due:
</b>
${bookingData.price}
</p>



<p>
Thank you for choosing 
Millrod Swim Academy!
</p>



</div>

`;

        document.getElementById("bookingForm").reset();

        updatePrice();
      } else {
        showMessage(result.error || "Unable to reserve lesson.", false);
      }
    } catch (error) {
      console.log(error);

      showMessage("Server error. Please try again.", false);
    }
  });
}

// ==============================
// LOAD BOOKED TIMES
// ==============================

// ==============================
// LOAD BOOKED TIMES
// ==============================

async function loadBookedSlots() {
  try {
    const response = await fetch("/booked-slots");

    const bookedSlots = await response.json();

    const dateInput = document.getElementById("lesson_date");

    const timeSelect = document.getElementById("lesson_time");

    function updateDisabledTimes() {
      const selectedDate = dateInput.value;

      Array.from(timeSelect.options).forEach((option) => {
        if (option.value) {
          option.disabled = false;

          option.textContent = option.value;
        }
      });

      bookedSlots.forEach((slot) => {
        if (slot.date === selectedDate) {
          Array.from(timeSelect.options).forEach((option) => {
            if (option.value === slot.time) {
              option.disabled = true;

              option.textContent = option.value + " (Booked)";
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
// AVAILABLE SCHEDULE DISPLAY
// ==============================

async function loadAvailableSchedule() {
  const scheduleBox = document.getElementById("availableSchedule");

  if (!scheduleBox) {
    return;
  }

  try {
    const response = await fetch("/booked-slots");

    const bookedSlots = await response.json();

    let html = "";

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

    for (let i = 0; i < 30; i++) {
      let date = new Date();

      date.setDate(today.getDate() + i);

      // Skip Sunday

      if (date.getDay() === 0) {
        continue;
      }

      let databaseDate = date.toISOString().split("T")[0];

      let displayDate = date.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
      });

      html += `

      <div class="schedule-day">

        <h4>
        ${displayDate}
        </h4>

        <div class="schedule-times">

      `;

      times.forEach((time) => {
        let booked = bookedSlots.some(
          (slot) => slot.date === databaseDate && slot.time === time,
        );

        if (booked) {
          html += `

          <button 
          class="time booked"
          disabled>

          🔴 ${time}
          <br>
          Booked

          </button>

          `;
        } else {
          html += `

          <button 
          class="time available"
          onclick="
          selectTime('${databaseDate}','${time}')
          ">

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

  document.getElementById("booking").scrollIntoView({
    behavior: "smooth",
  });
}

// LOAD EVERYTHING

document.addEventListener("DOMContentLoaded", () => {
  loadBookedSlots();

  loadAvailableSchedule();
});

// ==============================
// SHOW AVAILABLE SCHEDULE
// ==============================

async function loadAvailableSchedule() {
  const scheduleBox = document.getElementById("availableSchedule");

  try {
    const response = await fetch("/booked-slots");

    const bookedSlots = await response.json();

    const today = new Date();

    let html = "";

    for (let i = 0; i < 30; i++) {
      let date = new Date();

      date.setDate(today.getDate() + i);

      // Skip Sunday

      if (date.getDay() === 0) {
        continue;
      }

      let formattedDate = date.toISOString().split("T")[0];

      let displayDate = date.toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
      });

      html += `
      
      <div class="schedule-day">

        <h4>${displayDate}</h4>

        <p>Available Times:</p>

      `;

      let times = [
        "9:00 AM",
        "10:00 AM",
        "11:00 AM",
        "12:00 PM",
        "1:00 PM",
        "2:00 PM",
        "3:00 PM",
        "4:00 PM",
      ];

      times.forEach((time) => {
        let booked = bookedSlots.some(
          (slot) => slot.date === formattedDate && slot.time === time,
        );

        if (booked) {
          html += `
          <span class="time booked">
          ${time} - Booked
          </span>
          `;
        } else {
          html += `
          <span class="time available">
          ${time} - Available
          </span>
          `;
        }
      });

      html += `</div>`;
    }

    scheduleBox.innerHTML = html;
  } catch (error) {
    scheduleBox.innerHTML = "Unable to load schedule.";

    console.log(error);
  }
}

document.addEventListener("DOMContentLoaded", loadAvailableSchedule);
