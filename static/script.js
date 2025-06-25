/**
 * Chatbot UI Script
 * Author: Hashim
 * Description: Handles chat window toggle, session management, message sending, 
 * FastAPI backend integration, typing animation, and mobile navigation toggling.
 */

// ======================
// Global Variables
// ======================

let sessionId = null;  // Session ID assigned by FastAPI backend

// Loader animation HTML shown while waiting for bot response
const loaderHtml = `
  <div id="container">
    <div id="ball-1" class="circle"></div>
    <div id="ball-2" class="circle"></div>
    <div id="ball-3" class="circle"></div>
  </div>
`;

// Dynamic backend URL based on current domain (localhost or production)
const domain = window.location.origin;

// ======================
// Chat Window Logic
// ======================

/**
 * Toggles chat window visibility and triggers session fetch if first open.
 */
function toggleChat() {
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.classList.toggle("flex");
  chatWindow.classList.toggle("hidden");

  if (!sessionId) {
    fetchNewSession();
  }
}

/**
 * Fetches a new session ID from FastAPI backend.
 * Called once when chat opens for the first time.
 */
async function fetchNewSession() {
  try {
    const response = await fetch(`${domain}/session`);
    const data = await response.json();
    sessionId = data.session_id;
    console.log("Session ID:", sessionId);
  } catch (error) {
    console.error("Error fetching session ID:", error);
  }
}

// ======================
// Message Handling
// ======================

/**
 * Sends user message and handles bot response from backend.
 */
async function handleSend() {
  const chatInput = document.getElementById("chatInput");
  const userMessage = chatInput.value.trim();

  if (!userMessage) return;

  addMessageToChat(userMessage, "user");
  chatInput.value = "";

  const loadingMessageElement = addMessageToChat("...", "bot", true);

  try {
    const botResponse = await sendMessageToBot(userMessage);
    loadingMessageElement.remove();
    addMessageToChat(botResponse.response, "bot");
  } catch (error) {
    loadingMessageElement.remove();
    addMessageToChat("Sorry, there was an error connecting to the server.", "bot");
    console.error("Bot response error:", error);
  }
}

/**
 * Sends the message to the FastAPI backend with session ID.
 * @param {string} userMessage - Message entered by user
 * @returns {Object} response - Response JSON with chatbot reply
 */
async function sendMessageToBot(userMessage) {
  if (!sessionId) {
    throw new Error("Session ID is missing");
  }

  const response = await fetch(`${domain}/chat/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
  });

  return await response.json();
}

/**
 * Adds a chat message to the chat window.
 * @param {string} message - Text content of the message
 * @param {string} sender - 'user' or 'bot'
 * @param {boolean} isLoading - If true, shows loader instead of text
 * @returns {HTMLElement} - Reference to the message DOM element
 */
function addMessageToChat(message, sender, isLoading = false) {
  const chatBody = document.getElementById("chatBody");
  const messageElement = document.createElement("div");
  messageElement.className = `message ${sender}-message`;

  if (isLoading) {
    messageElement.classList.add("loading");
    messageElement.innerHTML = loaderHtml;
  } else {
    if (sender === "bot") {
      typeText(message, messageElement);
    } else {
      messageElement.textContent = message;
    }
  }

  chatBody.appendChild(messageElement);
  chatBody.scrollTop = chatBody.scrollHeight;
  return messageElement;
}

/**
 * Animates bot text output by typing it letter by letter.
 * @param {string} text - The bot's reply text
 * @param {HTMLElement} element - The DOM element to write into
 * @param {number} charactersPerStep - Number of characters per tick
 * @param {number} speed - Delay between characters (ms)
 */
function typeText(text, element, charactersPerStep = 2, speed = 50) {
  let index = 0;

  function type() {
    if (index < text.length) {
      element.textContent += text.substr(index, charactersPerStep);
      index += charactersPerStep;
      setTimeout(type, speed);
    }
  }

  type();
}

// ======================
// Event Listeners
// ======================

/**
 * Sends message on Enter key press.
 */
document.getElementById("chatInput").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    handleSend();
  }
});

/**
 * Toggles mobile navigation menu visibility.
 */
const mobileNavBtn = document.querySelector(".mobile-nav-btn");
const mobileNav = document.querySelector(".mobile-nav");

mobileNavBtn?.addEventListener("click", () => {
  mobileNav.classList.toggle("active");
});
