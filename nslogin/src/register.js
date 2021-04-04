import {library, dom} from '@fortawesome/fontawesome-svg-core/index.es.js';
import {
    faKey, faCheck, faInfoCircle, faExclamationTriangle, faUserPlus, faTimesCircle
} from '@fortawesome/free-solid-svg-icons/index.es.js';

library.add(
    faKey, faCheck, faTimesCircle, faInfoCircle, faExclamationTriangle, faUserPlus
);

import {
    clearPromptBox, showPromptBox
} from './prompt-box'

import { checkLogin, register } from './user'


document.addEventListener('DOMContentLoaded', () => {
    dom.watch();

    checkLogin().then(
        success => {
            if (success) {
                location.href = './';
            }
        }
    );

    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const userInput = document.getElementById('register-user');
    const invitationInput = document.getElementById('invitation');
    const submitBtn = document.getElementById('password-submit');

    submitBtn.addEventListener('click', () => {
        clearPromptBox();
        passwordInput.classList.remove("is-invalid");
        confirmPasswordInput.classList.remove("is-invalid");
        invitationInput.classList.remove("is-invalid");

        if (!(userInput.value && passwordInput.value && confirmPasswordInput.value)) {
            if (!userInput.value) {
                userInput.classList.add("is-invalid");
            }
            if (!passwordInput.value) {
                passwordInput.classList.add("is-invalid");
            }
            if (!confirmPasswordInput.value) {
                confirmPasswordInput.classList.add("is-invalid");
            }
            showPromptBox(
                "Invalid Input!",
                "Marked fields must not be empty.",
                "danger");
        } else if (confirmPasswordInput.value !== passwordInput.value) {
            showPromptBox(
                "Passwords Not Match!",
                "Passwords you typed are not the same.",
                "danger");
            confirmPasswordInput.classList.add("is-invalid");
            passwordInput.classList.add("is-invalid");
        } else {
            showPromptBox(
                "Submitting...",
                "Please wait for a second...",
                "info");
            register(userInput.value, passwordInput.value, invitationInput.value).then(
                resp => {
                    let success, error;
                    [success, error] = resp;
                    if (success) {
                        showPromptBox(
                            "Successfully Registered",
                            "Now you may log in with your account.",
                            "success");
                        location.href = './';
                    } else {
                        if (error === 'disabled'){
                            showPromptBox(
                                "Register failed!",
                                "Register is not enabled by this site.",
                                "danger");
                        } else if (error === 'invitation') {
                            showPromptBox(
                                "Register failed!",
                                "The invitation code you submitted is invalid.",
                                "danger");
                            invitationInput.classList.add("is-invalid");
                        } else if (error === 'duplicated') {
                            showPromptBox(
                                "Register failed!",
                                "This user name has been taken! Please use another user name.",
                                "danger");
                            userInput.classList.add("is-invalid");
                        } else {
                            showPromptBox(
                                "Register failed!",
                                "Unknown error occurred.",
                                "danger");

                        }
                    }
                }
            );
        }
    });
});
