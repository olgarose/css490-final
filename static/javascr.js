function confirmSubmit() {
  if (confirm("Are you sure you want to delete these contacts?")) {
    document.getElementById("FORM_ID").submit();
  }
  return false;
}