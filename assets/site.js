// Copy buttons and current-section highlighting in the section nav.

document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-copy]');
  if (!button) return;
  const source = document.getElementById(button.dataset.copy);
  const label = button.querySelector('span');
  const original = label.textContent;
  navigator.clipboard.writeText(source.textContent).then(() => {
    button.dataset.state = 'done';
    label.textContent = 'Copied';
  }, () => {
    label.textContent = 'Copy failed';
  }).finally(() => {
    setTimeout(() => {
      delete button.dataset.state;
      label.textContent = original;
    }, 2000);
  });
});

const navLinks = new Map(
  [...document.querySelectorAll('.toc a')].map((a) => [a.hash.slice(1), a])
);

if ('IntersectionObserver' in window && navLinks.size) {
  let current = null;
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const link = navLinks.get(entry.target.id);
      if (!link || link === current) continue;
      if (current) current.removeAttribute('aria-current');
      link.setAttribute('aria-current', 'true');
      current = link;
      const list = link.closest('ul');
      list.scrollTo({ left: link.parentElement.offsetLeft - 16, behavior: 'smooth' });
    }
  }, { rootMargin: '-30% 0px -60% 0px' });
  navLinks.forEach((_, id) => {
    const section = document.getElementById(id);
    if (section) observer.observe(section);
  });
}
