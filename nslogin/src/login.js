import {library, dom} from '@fortawesome/fontawesome-svg-core/index.es.js';
import {
  faKey, faCheck, faInfoCircle, faExclamationTriangle, faTimesCircle
} from '@fortawesome/free-solid-svg-icons/index.es.js';

library.add(
    faKey, faCheck, faTimesCircle, faInfoCircle, faExclamationTriangle
);

import {
    clearPromptBox, showPromptBox
} from './prompt-box';

import { login } from './user';

document.addEventListener('DOMContentLoaded', () => {
  dom.watch();

  const loginForm = document.getElementById('login-form');
  const userInput = document.getElementById('login-user');
  const passwordInput = document.getElementById('login-password');
  const submitBtn = document.getElementById('login-submit');
  const redirectInput = document.getElementById('login-redirect');
  const logoutStatus = document.getElementById('logout-status');

  loginForm.addEventListener("submit", function(evt) {
        evt.preventDefault();
    }, true);

  if (logoutStatus.value === 'True') {
      showPromptBox(
          "Successfully Logged Out",
          "You have successfully logged out.",
          "info");
  }

  submitBtn.addEventListener('click', () => {
      clearPromptBox();
      userInput.classList.remove("is-invalid");
      passwordInput.classList.remove("is-invalid");

      if (!(userInput.value && passwordInput.value)) {
          if (!userInput.value) {
              userInput.classList.add("is-invalid");
          }
          if (!passwordInput.value) {
              passwordInput.classList.add("is-invalid");
          }
          showPromptBox(
              "Invalid Input!",
              "User name and password must not be empty.",
              "danger");
      } else {
          showPromptBox(
              "Logging in...",
              "Please wait for a second...",
              "info");
          login(userInput.value, passwordInput.value).then(
              success => {
                  if (success) {
                      if (redirectInput.value) {
                          showPromptBox(
                              "Login Success",
                              "You will be redirect to the page you have requested.",
                              "success");
                          location.href = redirectInput.value;
                      } else {
                          showPromptBox(
                              "Login Success",
                              "Now you may access the restricted area.",
                              "success");
                          location.reload();
                      }
                  } else {
                      showPromptBox(
                          "Login Failed!",
                          "Please examine your user name and password.",
                          "danger");
                  }
              }
          );
      }
  });
});
