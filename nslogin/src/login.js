import {library, dom} from '@fortawesome/fontawesome-svg-core/index.es.js';
import {
  faKey, faCheck
} from '@fortawesome/free-solid-svg-icons/index.es.js';

import {
    faTimesCircle
} from '@fortawesome/free-regular-svg-icons/index.es.js';

library.add(
    faKey, faCheck, faTimesCircle
);

async function login(user, password) {
  const formData = new FormData();
  formData.append('user', user);
  formData.append('password', password);
  const response = await fetch('login',{
    method: 'POST',
    credentials: 'include',
    body: formData
  });
  return response.status === 200;
}

function showPromptBox(header, content, type='warning') {
    clearPromptBox();

    if (!type in ['warning', 'danger', 'success']) {
      return;
    }
    console.debug(`login-${type}-box`);
    let box = document.getElementById(`login-${type}-box`);
    let boxHeader = box.getElementsByClassName("box-title")[0];
    let boxContent = box.getElementsByClassName("box-content")[0];
    boxHeader.innerHTML = header;
    boxContent.innerHTML = content;
    box.style.display = "block";
}

function clearPromptBox() {
    for (let type of ['warning', 'danger', 'success']) {
        let box = document.getElementById(`login-${type}-box`);
        box.style.display = "none";
    }
}

document.addEventListener('DOMContentLoaded', () => {
  dom.watch();

  const userInput = document.getElementById('login-user');
  const passwordInput = document.getElementById('login-password');
  const submitBtn = document.getElementById('login-submit');
  const redirectInput = document.getElementById('login-redirect');

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
              "warning");
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
