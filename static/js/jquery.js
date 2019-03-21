document.getElementById("test").onclick = function() {
  if (CheckBoxCount()) {
    document.forms[0].submit();
  }
};

function CheckBoxCount() {
  var inputList = document.getElementsByTagName("input");
  var numChecked = 0;

  for (var i = 0; i < inputList.length; i++) {
    if (inputList[i].type == "checkbox" && inputList[i].checked) {
      numChecked = numChecked + 1;
    }
  }
  if (numChecked < 2) {
    alert("Minimum 2 !");
    return false;
  } else if (numChecked > 3) {
    alert("Maximum 3 !");
    return false;
  }
  alert("selected count: " + numChecked);

  return true;
}
