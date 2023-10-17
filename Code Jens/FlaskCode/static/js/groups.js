document.addEventListener('DOMContentLoaded', function () {
  const deviceButtons = document.querySelectorAll(".group-button");
  const deleteGroupButtons = document.querySelectorAll(".group-delete");

  deviceButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const group_id = button.getAttribute("group_id");
      console.log("Group ID:", group_id);
      updateUrlParameter("id", group_id);
    });
  });
  deleteGroupButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const group_id = button.getAttribute("group_id");
      console.log("Group ID:", group_id);
      updateUrlParameter("delete", group_id);
    });
  });

  const rows = document.querySelectorAll('.clickable-row');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            row.classList.toggle('selectedRow');
            const device_id = row.getAttribute("device_id");
            console.log("Device ID:", device_id);
            addParameterToURL("device", device_id);
            location.reload()
        });
    });
});

function addParameterToURL(paramName, paramValue) {
  const url = new URL(window.location.href);
  url.searchParams.set(paramName, paramValue);
  const updatedURL = url.toString();
  window.history.replaceState(null, document.title, updatedURL);
}

function updateUrlParameter(key, value) {
  const currentUrl = new URL(window.location.href);
  const searchParams = new URLSearchParams();

  // Add the new parameter
  searchParams.set(key, value);

  // Update the URL with the modified search parameters
  currentUrl.search = searchParams.toString();
  const newUrl = currentUrl.toString();

  // Redirect to the new URL
  window.location.href = newUrl;
}


if (window.location.search.includes("id=") || window.location.search.includes("delete=")) {
  if (window.location.search.includes("device=")) {
    window.location.href = window.location.href.split("&")[0]
  }
} else if (window.location.href.includes("?")) {
  const urlWithoutQuery = window.location.href.split("?")[0];
  window.history.replaceState(null, document.title, urlWithoutQuery);
}


const divElement = document.getElementById("newGroup");

divElement.addEventListener("click", function() {
  window.location.href = "groups?new=yes"
});