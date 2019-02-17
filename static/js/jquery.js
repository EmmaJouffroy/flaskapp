$("input[type=checkbox]").change(function(e) {
  if ($("input[type=checkbox]:checked").length > 3) {
    $(this).prop("checked", false);
    alert("allowed only 3");
  }
});
