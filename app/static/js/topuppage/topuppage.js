function changeSummary() {
  var desired_transaction = document.getElementById(
    "desired_transaction"
  ).value;
  var yenToPoint = document.getElementById("yen_to_point_ratio").value;
  var convertedValue = parseInt(desired_transaction) * parseFloat(yenToPoint);
  document.getElementById("obtained-point").textContent = convertedValue;
  document.getElementById("payment-amount").textContent = desired_transaction;
  document.getElementById("total-payment").textContent = desired_transaction;
}
