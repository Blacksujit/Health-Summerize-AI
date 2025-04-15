
$(document).ready(function(){
    document.querySelector('form').addEventListener('submit', function (e) {
        const fileInput = document.getElementById('fileInput');
        const textInput = document.getElementById('textInput');
        if (!fileInput.files.length && !textInput.value.trim()) {
            e.preventDefault();
            showPopup('Please upload a file or enter text for summarization.');
        }
    });

    function showPopup(message) {
        let timerInterval;
        Swal.fire({
            title: '⚠️⚠️Auto close alert!⚠️⚠️',
            html: message + ' I will close in <b></b> milliseconds.',
            timer: 2000,
            timerProgressBar: true,
            didOpen: () => {
                Swal.showLoading();
                const timer = Swal.getHtmlContainer().querySelector('b');
                timerInterval = setInterval(() => {
                    timer.textContent = Swal.getTimerLeft();
                }, 100);
            },
            willClose: () => {
                clearInterval(timerInterval);
            }
        }).then((result) => {
            if (result.dismiss === Swal.DismissReason.timer) {
                console.log('I was closed by the timer');
            }
        });
    }

    // GSAP Animations
    gsap.from('.header_section', { duration: 1, y: -50, opacity: 0, ease: 'power2.out' });
    gsap.from('.banner_content', { duration: 1, y: 50, opacity: 0, ease: 'power2.out', delay: 0.5 });
    gsap.from('.summarize_section h2', { duration: 1, y: 50, opacity: 0, ease: 'power2.out', delay: 0.7 });
    gsap.from('.summarize_section p', { duration: 1, y: 50, opacity: 0, ease: 'power2.out', delay: 0.9 });
    gsap.from('.form-group', { duration: 1, y: 50, opacity: 0, ease: 'power2.out', delay: 1.1, stagger: 0.2 });
    gsap.from('.btn-primary', { duration: 1, scale: 0.8, opacity: 0, ease: 'power2.out', delay: 1.3 });
    gsap.from('.img-fluid', { duration: 1, scale: 0.8, opacity: 0, ease: 'power2.out', delay: 1.5 });
});
 