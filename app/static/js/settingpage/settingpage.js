function displayPaperCutToken() {
  var x = document.getElementById("ppc-token");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}
