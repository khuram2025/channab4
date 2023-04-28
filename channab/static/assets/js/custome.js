// Datepicker script
$(document).ready(function() {
  $("#{{ form.dob.auto_id }}").datepicker({
    dateFormat: 'yy-mm-dd',
    changeMonth: true,
    changeYear: true,
    yearRange: "1900:2100"
  });
});

document.addEventListener("DOMContentLoaded", function() {
  const imageInput = document.getElementById("image-input");
  const dropzoneWrapper = document.getElementById("dropzone-desc");
  const imagePreview = document.getElementById("image-preview");

  dropzoneWrapper.addEventListener("click", function() {
    imageInput.click();
  });

  imageInput.addEventListener("change", function(event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = "block";
        dropzoneWrapper.style.display = "none";
      }
      reader.readAsDataURL(file);
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const deleteIcons = document.querySelectorAll('.delete-btn + .ri-delete-bin-line');

  deleteIcons.forEach(function(deleteIcon) {
    deleteIcon.addEventListener('click', function(event) {
      event.preventDefault();
      const deleteForm = deleteIcon.parentElement;
      const deleteUrl = deleteForm.getAttribute('data-delete-url');
      const deleteModalForm = document.getElementById('delete-modal-form');
      deleteModalForm.setAttribute('action', deleteUrl);
      const deleteModal = new bootstrap.Modal(document.getElementById('exampleModalToggle'), {});
      deleteModal.show();
    });
  });

  const cancelButton = document.querySelector('#exampleModalToggle .btn-md[data-bs-dismiss="modal"]');
  cancelButton.addEventListener('click', function() {
    const deleteModal = bootstrap.Modal.getInstance(document.getElementById('exampleModalToggle'));
    deleteModal.hide();
  });
});
