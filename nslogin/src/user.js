export async function checkLogin() {
    const response = await fetch('./auth',{
        method: 'GET',
        credentials: 'include'
    });
    console.log(response);
    return response.status === 200;
}

export async function login(user, password) {
    const formData = new FormData();
    formData.append('user', user);
    formData.append('password', password);
    const response = await fetch('.',{
        method: 'POST',
        credentials: 'include',
        body: formData
    });
    return response.status === 200;
}

export async function changePassword(user, oldPassword, newPassword) {
    const formData = new FormData();
    formData.append('user', user);
    formData.append('old-password', oldPassword);
    formData.append('new-password', newPassword);
    const response = await fetch('./changepassword',{
        method: 'POST',
        credentials: 'include',
        body: formData
    });
    return response.status === 200;
}

export async function register(user, password, invitation='') {
    const formData = new FormData();
    formData.append('user', user);
    formData.append('password', password);
    formData.append('invitation', invitation);
    const response = await fetch('./register',{
        method: 'POST',
        credentials: 'include',
        body: formData
    });

    if (response.status === 200) {
        return [true, ''];
    } else {
        const msg = await response.text();
        return [false, msg];
    }
}

export async function logout() {
    const response = await fetch('./logout',{
        method: 'GET',
        credentials: 'include'
    });
    return response.status === 200;
}

