function displayPaperCutToken() {
  var x = document.getElementById("ppc-token");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function displayPaypayAPIKey() {
  var x = document.getElementById("paypay_api_key");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function displayPaypayAPISecret() {
  var x = document.getElementById("paypay_api_secret");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function displayPaypayMerchantId() {
  var x = document.getElementById("paypay_merchant_id");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function changeConversionSimulation() {
  var minimumPurchase = document.getElementById("minimum_purchase").value;
  var yenToPoint = document.getElementById("yen_to_point").value;
  var convertedValue = parseInt(minimumPurchase) * parseInt(yenToPoint);
  var lang = document.getElementById("lang2").value;
  var displayedValue = "";
  if (lang == "en") {
    displayedValue = minimumPurchase + "￥ = " + convertedValue + " Points";
  } else {
    displayedValue = minimumPurchase + "￥ = " + convertedValue + " ポイント";
  }
  document.getElementById("yen_to_point_simulation").value = displayedValue;
}

function setCheckboxValue() {
  var paypayChecked = document
    .getElementById("paypay_enabled")
    .getAttribute("checked");
  console.log(paypayChecked);
}
