function confirmSubmit() {
  if (confirm("Are you sure you want to delete selected?")) {
    document.getElementById("FORM_ID").submit();
  }
  return false;
}