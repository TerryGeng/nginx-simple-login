export function showPromptBox(header, content, type='info') {
    clearPromptBox();

    if (!type in ['warning', 'danger', 'success', 'info']) {
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

export function clearPromptBox() {
    for (let type of ['warning', 'danger', 'success', 'info']) {
        let box = document.getElementById(`login-${type}-box`);
        box.style.display = "none";
    }
}

