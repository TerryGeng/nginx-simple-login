import {library, dom} from '@fortawesome/fontawesome-svg-core/index.es.js';
import {
    faExchangeAlt, faDoorOpen, faHouseUser
} from '@fortawesome/free-solid-svg-icons/index.es.js';

import { logout } from './user'

library.add(
    faExchangeAlt, faDoorOpen, faHouseUser
);


document.addEventListener('DOMContentLoaded', () => {
    dom.watch();

    const logoutBtn = document.getElementById('logout');

    logoutBtn.addEventListener('click', () => {
        logout().then(
            success => {
                location.href = '?logout=True';
            }
        );
    });
});
