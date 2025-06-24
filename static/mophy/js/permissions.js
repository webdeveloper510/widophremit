// // permissions.js

// function applyPermissions() {
//     // Get the "Add" button element
//     var addButton = document.querySelector('#add-permission-button');
//     var permissions = document.querySelector('.permissions');

//     // Check if the user is an admin
//     var isAdmin = permissions.getAttribute('data-is-admin');

//     var group_permission = permissions.getAttribute('data-group-permission');

//     // Check if the user has the required permission
//     var hasPermission = permissions.getAttribute('data-add-btn-permission');
//     console.log(group_permission, "group_permission", isAdmin, "isAdmin", hasPermission, "hasPermission");

//     // Convert the string value of hasPermission to a boolean
//     hasPermission = hasPermission.toLowerCase() === 'true';

//     // Show or hide the "Add" button based on conditions
//     if (isAdmin === 'true') {
//         console.log("true is admin");
//         addButton.style.display = "block"; // Show the button
//     }
//     else if (hasPermission === true ){
//         addButton.style.display = "block"; // show the button
//     }
//     else{
//         addButton.style.display = "none"; // show the button
//     }
// }

// // Call the function when the document is ready
// document.addEventListener("DOMContentLoaded", function() {
//     applyPermissions();
// });
