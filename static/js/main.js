// SnapLink — Main JavaScript

// Navbar scroll effect
const navbar = document.getElementById('main-navbar');
if (navbar) {
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const current = window.pageYOffset;
        if (current > 80) {
            navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        lastScroll = current;
    }, { passive: true });
}

// Animate counters
function animateCounter(el, target, duration = 1200) {
    if (!el || target === 0) return;
    let start = 0;
    const step = (timestamp) => {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

// Run counter animations on home page
document.addEventListener('DOMContentLoaded', () => {
    const totalUrls = document.getElementById('stat-total-urls');
    const totalClicks = document.getElementById('stat-total-clicks');
    const activeUrls = document.getElementById('stat-active-urls');

    if (totalUrls) animateCounter(totalUrls, parseInt(totalUrls.textContent) || 0);
    if (totalClicks) animateCounter(totalClicks, parseInt(totalClicks.textContent) || 0);
    if (activeUrls) animateCounter(activeUrls, parseInt(activeUrls.textContent) || 0);

    // Intersection Observer for feature cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, i * 80);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .link-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(card);
    });

    // URL input validation feedback
    const urlInput = document.getElementById('original-url-input');
    if (urlInput) {
        urlInput.addEventListener('input', () => {
            urlInput.classList.remove('input-error');
            const errorEl = urlInput.parentNode.querySelector('.field-error');
            if (errorEl) errorEl.remove();
        });

        // Paste enhancement - auto-focus after paste
        urlInput.addEventListener('paste', () => {
            setTimeout(() => {
                if (urlInput.value.trim()) {
                    urlInput.style.borderColor = 'var(--purple)';
                    setTimeout(() => urlInput.style.borderColor = '', 500);
                }
            }, 100);
        });
    }

    // Auto-dismiss messages after 4 seconds
    setTimeout(() => {
        const msgs = document.querySelectorAll('.message');
        msgs.forEach(msg => {
            msg.style.transition = 'opacity 0.3s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        });
    }, 4000);
});

// Global copyText utility (used across pages)
window.copyText = function(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard!'));
    } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('Copied!');
    }
};

window.showToast = function(msg) {
    // Remove existing toast
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        requestAnimationFrame(() => toast.classList.add('show'));
    });

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2200);
};
