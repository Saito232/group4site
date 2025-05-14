//This script will automatically hide the toast message after 3 seconds
  setTimeout(() => {
    const toasts = document.querySelectorAll('[id^="toast-"]');
    toasts.forEach(toast => {
      toast.style.display = 'none';
    });
  }, 3000);

