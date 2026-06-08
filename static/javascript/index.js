document.addEventListener('DOMContentLoaded', function () {

    const flashes = document.querySelectorAll('.alert');

    flashes.forEach(function (flash) {

        setTimeout(() => {

            flash.style.transition = 'opacity 0.5s ease';

            flash.style.opacity = '0';

            setTimeout(() => {

                flash.remove();

            }, 500);

        }, 4000);

    });

});