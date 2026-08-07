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
