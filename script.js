// ===== STATE =====
let currentInput = "";    // What user is currently typing
let previousInput = "";   // First number (saved when operator pressed)
let operator = null;      // Current operation (+, -, *, /)
 
// ===== DOM ELEMENTS =====
const currentDisplay  = document.getElementById("current");
const previousDisplay = document.getElementById("previous");
 
// ===== UPDATE DISPLAY =====
function updateDisplay() {
  currentDisplay.textContent = currentInput || "0";
  previousDisplay.textContent = previousInput
    ? `${previousInput} ${getOperatorSymbol(operator)}`
    : "";
}
 
function getOperatorSymbol(op) {
  const symbols = { "+": "+", "-": "−", "*": "×", "/": "÷", "%": "%" };
  return symbols[op] || "";
}
 
// ===== INPUT A DIGIT =====
function inputDigit(digit) {
  // Prevent multiple decimal points
  if (digit === "." && currentInput.includes(".")) return;
 
  // Prevent leading zeros (but allow "0.")
  if (currentInput === "0" && digit !== ".") {
    currentInput = digit;
  } else {
    currentInput += digit;
  }
  updateDisplay();
}
 
// ===== INPUT AN OPERATOR =====
function inputOperator(op) {
  // If there's a pending operation and user typed a new number, compute first
  if (operator && currentInput) {
    calculate();
  }
 
  // Save current number and set the operator
  if (currentInput) {
    previousInput = currentInput;
    currentInput = "";
  }
  operator = op;
  updateDisplay();
}
 
// ===== CALCULATE =====
function calculate() {
  if (!previousInput || !currentInput || !operator) return;
 
  const prev = parseFloat(previousInput);
  const curr = parseFloat(currentInput);
  let result;
 
  switch (operator) {
    case "+": result = prev + curr; break;
    case "-": result = prev - curr; break;
    case "*": result = prev * curr; break;
    case "/":
      if (curr === 0) {
        currentInput = "Error";
        previousInput = "";
        operator = null;
        updateDisplay();
        return;
      }
      result = prev / curr;
      break;
    case "%": result = prev % curr; break;
    default: return;
  }
 
  // Format result: avoid super long decimals
  currentInput = String(
    parseFloat(result.toFixed(10))  // Max 10 decimal places, strip trailing 0s
  );
  previousInput = "";
  operator = null;
  updateDisplay();
}
 
// ===== CLEAR & DELETE =====
function clearAll() {
  currentInput = "";
  previousInput = "";
  operator = null;
  updateDisplay();
}
 
function deleteLast() {
  currentInput = currentInput.slice(0, -1);
  updateDisplay();
}
 
// ===== EVENT LISTENERS =====
// Number buttons
document.querySelectorAll(".num").forEach(btn => {
  btn.addEventListener("click", () => inputDigit(btn.dataset.num));
});
 
// Operator buttons
document.querySelectorAll(".op").forEach(btn => {
  btn.addEventListener("click", () => inputOperator(btn.dataset.op));
});
 
// Equals, Clear, Delete
document.querySelector(".equals").addEventListener("click", calculate);
document.querySelector(".clear").addEventListener("click", clearAll);
document.querySelector(".delete").addEventListener("click", deleteLast);
 
// ===== KEYBOARD SUPPORT =====
document.addEventListener("keydown", (e) => {
  if (e.key >= "0" && e.key <= "9" || e.key === ".") inputDigit(e.key);
  else if (e.key === "+") inputOperator("+");
  else if (e.key === "-") inputOperator("-");
  else if (e.key === "") inputOperator("");
  else if (e.key === "/") { e.preventDefault(); inputOperator("/"); }
  else if (e.key === "Enter" || e.key === "=") calculate();
  else if (e.key === "Escape") clearAll();
  else if (e.key === "Backspace") deleteLast();
});