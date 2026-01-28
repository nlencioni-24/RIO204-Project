function goHome() { window.location.href = 'dashboard.html'; }

// --- Occupancy dynamique ---
let currentOccupancy = 0;
const maxPartial = 20;
const availabilityElem = document.getElementById('availability');
const occupancyElem = document.getElementById('occupancy');
const inBadge = document.getElementById('inBadge');
const inRoomBtn = document.getElementById('inRoomBtn');

function updateOccupancyDisplay() {
  occupancyElem.textContent = currentOccupancy + " people";

  // Priority to Schedule
  if (window.currentScheduleClass) {
    if (availabilityElem) {
      availabilityElem.textContent = "🔴 Occupied (" + window.currentScheduleClass + ")";
      availabilityElem.className = "occupied";
    }
    return;
  }


  if (currentOccupancy === 0) {
    availabilityElem.textContent = "🟢 Free";
    availabilityElem.className = "free";
  } else if (currentOccupancy <= maxPartial) {
    availabilityElem.textContent = "🟠 Partial";
    availabilityElem.className = "partial";
  } else {
    availabilityElem.textContent = "🔴 Occupied";
    availabilityElem.className = "occupied";
  }
}

// --- Toast function ---
function showToast(message, color = "#2ecc71") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.backgroundColor = color;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 5000);
}

// --- Reward function ---
// --- Reward function ---
async function addRewardPoints(points) {
  try {
    const res = await fetch('/api/rewards/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ points: points })
    });
    const data = await res.json();
    if (data.success) {
      return data.points;
    } else {
      console.warn("Could not add points:", data.message);
      // Fallback local or return 0
      return 0; // Or keep local storage as fallback? No, requirement is DB.
    }
  } catch (e) {
    console.error("Error adding points:", e);
    return 0;
  }
}

function showBadge(score) {
  // ... (Keep existing logic, maybe fetch badges from DB later, but for now local checks on score are fine if we get correct score)
  let badgesSeen = JSON.parse(localStorage.getItem("badgesSeen")) || [];

  if (score >= 10 && !badgesSeen.includes("🥉 Contributor")) {
    showToast("Badge unlocked: 🥉 Contributor!");
    badgesSeen.push("🥉 Contributor");
  }
  if (score >= 50 && !badgesSeen.includes("🥈 Active Helper")) {
    showToast("Badge unlocked: 🥈 Active Helper!");
    badgesSeen.push("🥈 Active Helper");
  }
  if (score >= 100 && !badgesSeen.includes("🥇 Super User")) {
    showToast("Badge unlocked: 🥇 Super User!");
    badgesSeen.push("🥇 Super User");
  }
  if (score >= 200 && !badgesSeen.includes("🏆 Campus Hero")) {
    showToast("Badge unlocked: 🏆 Campus Hero!");
    badgesSeen.push("🏆 Campus Hero");
  }

  localStorage.setItem("badgesSeen", JSON.stringify(badgesSeen));
}

// --- Boutons "I am in / I left" ---
// --- API Wrapper for Occupancy ---
async function updateServerOccupancy(action, value = null) {
  if (!window.currentRoomId) return;
  try {
    const res = await fetch(`/api/room/${window.currentRoomId}/occupancy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: action, value: value })
    });
    const data = await res.json();
    if (data.success) {
      if (currentOccupancy !== data.occupancy) {
        currentOccupancy = data.occupancy;
        updateOccupancyDisplay();
      }
    }
  } catch (e) {
    console.error("Error updating occupancy:", e);
  }
}

// --- Boutons "I am in / I left" ---
async function enterRoom() {
  await updateServerOccupancy('enter');

  if (inBadge) inBadge.style.display = "inline";
  if (inRoomBtn) {
    inRoomBtn.textContent = "✅ In the room";
    inRoomBtn.disabled = true;
    inRoomBtn.classList.add("in-room-active");
  }

  // Ajouter 10 points au score global
  let score = await addRewardPoints(10);

  if (score > 0) {
    // Afficher notification toast
    showToast(`🎉+10 points! Total score: ${score}`);

    // Vérifier badge
    showBadge(score);
  } else {
    showToast(`🎉 Thanks for contributing! (Login to earn points)`);
  }
}

async function leaveRoom() {
  await updateServerOccupancy('leave');

  if (inBadge) inBadge.style.display = "none";
  if (inRoomBtn) {
    inRoomBtn.textContent = "I am in this room";
    inRoomBtn.disabled = false;
    inRoomBtn.classList.remove("in-room-active");
  }
}

// --- Make a change ---
function makeChange() {
  if (!inRoomBtn.disabled) {
    showToast("⚠️ You must be IN the room to change occupancy", "#e74c3c");
    return;
  }
  // Affiche la modal
  document.getElementById("occupancyModal").style.display = "flex";
  document.getElementById("newOccupancyInput").value = currentOccupancy; // valeur par défaut
  document.getElementById("newOccupancyInput").focus();
}

function closeOccupancyModal() {
  document.getElementById("occupancyModal").style.display = "none";
}

// Valider le nouveau nombre
async function submitOccupancyChange() {
  const input = document.getElementById("newOccupancyInput");
  let newOccupancy = parseInt(input.value);
  if (!isNaN(newOccupancy) && newOccupancy >= 0) {
    await updateServerOccupancy('set', newOccupancy);
    showToast(`✅ Occupancy updated to ${newOccupancy} people`);
    closeOccupancyModal();
  } else {
    showToast("❌ Please enter a valid number >= 0", "#e74c3c");
  }
}


// Initial display
updateOccupancyDisplay();

// --- Exposed logic for dynamic rooms ---
// --- Exposed logic for dynamic rooms ---
window.setCurrentRoomId = function (id) {
  window.currentRoomId = id;
  console.log("Room context set to:", id);
  // Initial fetch
  fetchRoomStatus();
};

async function fetchRoomStatus() {
  if (!window.currentRoomId) return;
  try {
    const res = await fetch(`/api/room/${window.currentRoomId}/status`);
    const data = await res.json();
    if (data.success && data.occupancy !== undefined) {
      if (currentOccupancy !== data.occupancy) {
        currentOccupancy = data.occupancy;
        updateOccupancyDisplay();
      }
    }
  } catch (e) { console.error(e); }
}

// Poll every 5 seconds
setInterval(fetchRoomStatus, 5000);

// --- Expose functions to global scope for HTML onclick attributes ---
window.goHome = goHome;
window.enterRoom = enterRoom;
window.leaveRoom = leaveRoom;
window.makeChange = makeChange;
window.submitOccupancyChange = submitOccupancyChange;
window.closeOccupancyModal = closeOccupancyModal;

window.setCurrentOccupancy = function (val) {
  currentOccupancy = val;
  updateOccupancyDisplay();
};

// --- Sensors.js update for other values ---
// Removed fixed interval here to avoid conflict with room.html logic
// function updateSensorsDisplay() { ... }