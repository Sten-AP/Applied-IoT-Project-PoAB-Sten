document.addEventListener('DOMContentLoaded', function () {
  const deviceButtons = document.querySelectorAll(".device-button");

  deviceButtons.forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const device_id = button.getAttribute("device_id");
      console.log("Device ID:", device_id);
      updateUrlParameter("id", device_id);
    });
  });

  const onButton = document.getElementById('on');

  onButton.addEventListener('click', function() {
    addParameterToURL("lights", "on")
    location.reload()
  });

  const offButton = document.getElementById('off');

  offButton.addEventListener('click', function() {
    addParameterToURL("lights", "off")
    location.reload()
  });

  const autoButton = document.getElementById('auto');

  autoButton.addEventListener('click', function() {
    addParameterToURL("lights", "auto")
    location.reload()
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

if (window.location.href.includes("&")) {
  const urlWithoutQuery = window.location.href.split("&")[0];
  window.history.replaceState(null, document.title, urlWithoutQuery);
}
