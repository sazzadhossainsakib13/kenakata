/* ============================================
   KenaKata — Main JavaScript
   ============================================ */

// ============================================
// CART FUNCTIONALITY
// ============================================
function addToCart(productId, quantity = 1) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

  fetch(`/cart/add/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${quantity}`,
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      updateCartCount(data.cart_count);
      animateCartIcon();
    } else {
      showToast(data.message || 'Something went wrong.', 'error');
    }
  })
  .catch(() => showToast('Failed to add to cart.', 'error'));
}

function updateCartCount(count) {
  document.querySelectorAll('.cart-count-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

function animateCartIcon() {
  const cartBtn = document.querySelector('.cart-nav-btn');
  if (cartBtn) {
    cartBtn.classList.add('cart-bounce');
    setTimeout(() => cartBtn.classList.remove('cart-bounce'), 600);
  }
}

// ============================================
// WISHLIST FUNCTIONALITY
// ============================================
function toggleWishlist(productId, btn) {
  const isInWishlist = btn.classList.contains('active');
  const url = isInWishlist
    ? `/wishlist/remove/${productId}/`
    : `/wishlist/add/${productId}/`;

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      btn.classList.toggle('active');
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = btn.classList.contains('active') ? 'bi bi-heart-fill' : 'bi bi-heart';
      }
      animateWishlistBtn(btn);
      updateWishlistCount(data.wishlist_count);
      showToast(data.message, 'success');
    }
  })
  .catch(() => {
    // Redirect to login if not authenticated
    window.location.href = `/auth/login/?next=${window.location.pathname}`;
  });
}

function animateWishlistBtn(btn) {
  btn.style.transform = 'scale(1.4)';
  setTimeout(() => btn.style.transform = 'scale(1)', 300);
}

function updateWishlistCount(count) {
  document.querySelectorAll('.wishlist-count-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'success', duration = 3000) {
  let container = document.querySelector('.kk-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'kk-toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill',
  };

  const toast = document.createElement('div');
  toast.className = `kk-toast ${type}`;
  toast.innerHTML = `
    <i class="bi ${icons[type] || icons.info}"></i>
    <span>${message}</span>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;color:inherit;cursor:pointer;margin-left:8px;opacity:0.6;font-size:16px;">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ============================================
// FLASH SALE COUNTDOWN
// ============================================
function initCountdown(endTimeStr) {
  const endTime = new Date(endTimeStr).getTime();

  function update() {
    const now = new Date().getTime();
    const diff = endTime - now;

    if (diff <= 0) {
      document.querySelectorAll('.countdown-num').forEach(el => el.textContent = '00');
      return;
    }

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    const hEl = document.getElementById('countdown-hours');
    const mEl = document.getElementById('countdown-minutes');
    const sEl = document.getElementById('countdown-seconds');

    if (hEl) hEl.textContent = String(hours).padStart(2, '0');
    if (mEl) mEl.textContent = String(minutes).padStart(2, '0');
    if (sEl) sEl.textContent = String(seconds).padStart(2, '0');
  }

  update();
  setInterval(update, 1000);
}

// ============================================
// CART QUANTITY CONTROLS
// ============================================
function initQtyControls() {
  document.querySelectorAll('.qty-control').forEach(control => {
    const minusBtn = control.querySelector('.qty-minus');
    const plusBtn = control.querySelector('.qty-plus');
    const input = control.querySelector('.qty-input');

    if (!input) return;

    if (minusBtn) {
      minusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) - 1;
        if (val < 1) val = 1;
        input.value = val;
        input.dispatchEvent(new Event('change'));
      });
    }

    if (plusBtn) {
      plusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) + 1;
        const max = parseInt(input.max) || 99;
        if (val > max) val = max;
        input.value = val;
        input.dispatchEvent(new Event('change'));
      });
    }
  });
}

// ============================================
// NAVBAR SCROLL BEHAVIOR
// ============================================
function initNavbarScroll() {
  const navbar = document.querySelector('.kk-navbar');
  if (!navbar) return;
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

// ============================================
// BACK TO TOP
// ============================================
function initBackToTop() {
  const btn = document.querySelector('.back-to-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 300);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ============================================
// GALLERY THUMBNAILS
// ============================================
function initGallery() {
  const thumbs = document.querySelectorAll('.gallery-thumb');
  const mainImg = document.querySelector('.gallery-main img');

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      if (mainImg) {
        mainImg.style.opacity = '0';
        setTimeout(() => {
          mainImg.src = thumb.dataset.full || thumb.querySelector('img')?.src;
          mainImg.style.opacity = '1';
        }, 150);
      }
    });
  });

  // Animate image opacity
  if (mainImg) {
    mainImg.style.transition = 'opacity 0.15s ease';
  }
}

// ============================================
// AUTO-DISMISS MESSAGES
// ============================================
function initMessages() {
  document.querySelectorAll('.message-alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      alert.style.transition = 'all 0.3s ease';
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });
}

// ============================================
// CART PAGE - LIVE UPDATES
// ============================================
function initCartPage() {
  document.querySelectorAll('.cart-qty-input').forEach(input => {
    let debounce;
    input.addEventListener('change', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        const itemId = input.dataset.itemId;
        const qty = input.value;
        updateCartItem(itemId, qty, input);
      }, 500);
    });
  });
}

function updateCartItem(itemId, qty, input) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${qty}`,
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      // Update item subtotal
      const row = input.closest('tr') || input.closest('.cart-item');
      if (row) {
        const subtotalEl = row.querySelector('.item-subtotal');
        if (subtotalEl) subtotalEl.textContent = `৳${parseFloat(data.item_total).toLocaleString('bn-BD')}`;
      }
      // Update cart total
      const subtotalEl = document.getElementById('cart-subtotal');
      if (subtotalEl) subtotalEl.textContent = `৳${parseFloat(data.cart_subtotal).toLocaleString()}`;
      updateCartCount(data.cart_count);
    }
  });
}

function removeCartItem(itemId) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1];

  fetch(`/cart/remove/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const row = document.querySelector(`[data-item-id="${itemId}"]`)?.closest('tr') ||
                  document.querySelector(`[data-item-id="${itemId}"]`)?.closest('.cart-item');
      if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'all 0.3s ease';
        setTimeout(() => { row.remove(); refreshCartTotals(); }, 300);
      }
      updateCartCount(data.cart_count);
      showToast(data.message, 'success');
    }
  });
}

function refreshCartTotals() {
  // Simple page reload for cart totals after remove
  window.location.reload();
}

// ============================================
// FADE IN ANIMATIONS (INTERSECTION OBSERVER)
// ============================================
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in-up').forEach(el => observer.observe(el));
}

// ============================================
// MOBILE SEARCH TOGGLE
// ============================================
function initMobileSearch() {
  const searchToggle = document.querySelector('.mobile-search-toggle');
  const searchBox = document.querySelector('.mobile-search-box');
  if (!searchToggle || !searchBox) return;

  searchToggle.addEventListener('click', () => {
    searchBox.classList.toggle('show');
    if (searchBox.classList.contains('show')) {
      searchBox.querySelector('input')?.focus();
    }
  });
}

// ============================================
// PRODUCT QUANTITY SELECTOR (PRODUCT DETAIL)
// ============================================
function initProductQty() {
  const qtyInput = document.getElementById('product-qty');
  const minusBtn = document.getElementById('qty-minus');
  const plusBtn = document.getElementById('qty-plus');
  if (!qtyInput) return;

  const maxStock = parseInt(qtyInput.max) || 99;

  minusBtn?.addEventListener('click', () => {
    let v = parseInt(qtyInput.value);
    if (v > 1) qtyInput.value = v - 1;
  });

  plusBtn?.addEventListener('click', () => {
    let v = parseInt(qtyInput.value);
    if (v < maxStock) qtyInput.value = v + 1;
  });
}

// ============================================
// INITIALIZE ALL
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initBackToTop();
  initGallery();
  initMessages();
  initCartPage();
  initQtyControls();
  initScrollAnimations();
  initMobileSearch();
  initProductQty();
  initAddToCartForms();

  // Cart bounce keyframe
  const style = document.createElement('style');
  style.textContent = `
    @keyframes cartBounce {
      0% { transform: scale(1); }
      30% { transform: scale(1.3); }
      60% { transform: scale(0.9); }
      100% { transform: scale(1); }
    }
    .cart-bounce { animation: cartBounce 0.6s ease; }
  `;
  document.head.appendChild(style);
});

// Global delegated listener for add-to-cart-form submit
function initAddToCartForms() {
  document.addEventListener('submit', function(e) {
    const form = e.target.closest('.add-to-cart-form');
    if (form) {
      e.preventDefault();
      const url = form.action;
      const qty = form.querySelector('input[name="quantity"]')?.value || 1;
      const productId = url.match(/\/cart\/add\/(\d+)\//)?.[1];
      if (productId) addToCart(productId, qty);
    }
  });
}
