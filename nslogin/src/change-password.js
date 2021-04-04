import {library, dom} from '@fortawesome/fontawesome-svg-core/index.es.js';
import {
    faKey, faCheck, faInfoCircle, faExclamationTriangle, faTimesCircle, faChevronLeft
} from '@fortawesome/free-solid-svg-icons/index.es.js';

library.add(
    faKey, faCheck, faTimesCircle, faInfoCircle, faExclamationTriangle, faChevronLeft
);

import {
    clearPromptBox, showPromptBox
} from './prompt-box'

import { login, checkLogin, changePassword } from './user'


document.addEventListener('DOMContentLoaded', () => {
    dom.watch();

    checkLogin().then(
        success => {
            if (!success) {
                location.href = './';
            }
        }
    );

    const oldPasswordInput = document.getElementById('old-password');
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const userInput = document.getElementById('user');
    const submitBtn = document.getElementById('password-submit');

    submitBtn.addEventListener('click', () => {
        clearPromptBox();
        oldPasswordInput.classList.remove("is-invalid");
        newPasswordInput.classList.remove("is-invalid");
        confirmPasswordInput.classList.remove("is-invalid");

        if (!(newPasswordInput.value && oldPasswordInput.value && confirmPasswordInput.value)) {
            if (!newPasswordInput.value) {
                newPasswordInput.classList.add("is-invalid");
            }
            if (!oldPasswordInput.value) {
                oldPasswordInput.classList.add("is-invalid");
            }
            if (!confirmPasswordInput.value) {
                confirmPasswordInput.classList.add("is-invalid");
            }
            showPromptBox(
                "Invalid Input!",
                "Old, new passwords must not be empty.",
                "danger");
        } else if (confirmPasswordInput.value !== newPasswordInput.value) {
            showPromptBox(
                "Passwords Not Match!",
                "New passwords you typed are not the same.",
                "danger");
                confirmPasswordInput.classList.add("is-invalid");
                newPasswordInput.classList.add("is-invalid");
        } else {
            showPromptBox(
                "Submitting...",
                "Please wait for a second...",
                "info");
            login(userInput.value, oldPasswordInput.value).then(
                success => {
                    if (success) {
                        changePassword(userInput.value, oldPasswordInput.value,
                            newPasswordInput.value).then(
                                success => {
                                    if (success) {
                                        showPromptBox(
                                            "Password Changes",
                                            "Now you may log in with your new password.",
                                            "success");
                                    } else {
                                        showPromptBox(
                                            "Unknown Error",
                                            "Unknown error occurred.",
                                            "danger");
                                    }
                                }
                        );
                    } else {
                        oldPasswordInput.classList.add("is-invalid");
                        showPromptBox(
                            "Wrong Password!",
                            "Please examine your old password.",
                            "danger");
                    }
                }
            );
        }
    });
});
