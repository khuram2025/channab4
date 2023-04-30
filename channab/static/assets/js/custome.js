// Datepicker script
$(document).ready(function () {
  $("#dob-input").datepicker({
    dateFormat: "yy-mm-dd",
    changeMonth: true,
    changeYear: true,
    yearRange: "1900:2100",
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const imageInput = document.getElementById("image-input");
  const dropzoneWrapper = document.getElementById("dropzone-desc");
  const imagePreview = document.getElementById("image-preview");

  dropzoneWrapper.addEventListener("click", function () {
    imageInput.click();
  });

  imageInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = "block";
        dropzoneWrapper.style.display = "none";
      };
      reader.readAsDataURL(file);
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  var editMilkModal = new bootstrap.Modal(document.getElementById("editMilk"), {});
  editMilkModal.show();
});

$(document).ready(function () {
  var dateInput = $("#date-input");
  var animalId = dateInput.data("animal-id");
  var getMilkRecordUrl = dateInput.data("get-milk-record-url");
  var secondTimeInputId = dateInput.data("second-time-input-id");
  var thirdTimeInputId = dateInput.data("third-time-input-id");

  dateInput.datepicker({
    dateFormat: "yy-mm-dd",
    changeMonth: true,
    changeYear: true,
    yearRange: "1900:2100",
    onSelect: function (dateText) {
      var selectedDate = dateText;
      var url = '{% url "dairy:get_milk_record" animal.id "0000-00-00" %}'.replace("0000-00-00", selectedDate);

      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          if (data) {
            document.getElementById("{{ form.first_time.auto_id }}").value = data.first_time;
            document.getElementById("{{ form.second_time.auto_id }}").value = data.second_time;
            document.getElementById("{{ form.third_time.auto_id }}").value = data.third_time;
          } else {
            document.getElementById("{{ form.first_time.auto_id }}").value = "";
            document.getElementById("{{ form.second_time.auto_id }}").value = "";
            document.getElementById("{{ form.third_time.auto_id }}").value = "";
          }
        })
        .catch((error) => {
          console.error("Error fetching milk record data:", error);
        });
    },
  });
});
