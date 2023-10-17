const sidebarDevice = document.getElementById("sidebar-devices");
const sidebarGroups = document.getElementById("sidebar-groups");
const sidebarAllDevices = document.getElementById("sidebar-allDevices");

sidebarDevice.addEventListener("click", function(event) {
  window.parent.location.href = "/devices"
});

sidebarGroups.addEventListener("click", function(event) {
  window.parent.location.href = "/groups"
});

sidebarAllDevices.addEventListener("click", function(event) {
  window.parent.location.href = "/alldevices"
});