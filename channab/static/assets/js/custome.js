document.addEventListener("DOMContentLoaded", function() {
  const imageInput = document.getElementById("image-input");
  const dropzoneWrapper = document.getElementById("dropzone-desc"); // Change the ID here
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
        dropzoneWrapper.style.display = "none"; // Also update the ID here
      }
      reader.readAsDataURL(file);
    }
  });
});


document.addEventListener('DOMContentLoaded', function () {
    var editAnimalModal = new bootstrap.Modal(document.getElementById('editAnimal'), {});
    editAnimalModal.show();
});

document.getElementById('submit-form').addEventListener('click', function () {
    document.getElementById('animal-form').submit();
});
<script>
        document.addEventListener('DOMContentLoaded', function () {
            var editAnimalModal = new bootstrap.Modal(document.getElementById('editAnimal'), {});
            editAnimalModal.show();
        });
    </script>
    <script>
$(document).ready(function() {
    $("#{{ form.dob.auto_id }}").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: "1900:2100"
    });
});
</script>
