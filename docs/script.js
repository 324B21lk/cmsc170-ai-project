const links = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('main section[id]');
const progress = document.getElementById('scroll-progress');

function updateProgress() {
  const total = document.documentElement.scrollHeight - window.innerHeight;
  const amount = total > 0 ? (window.scrollY / total) * 100 : 0;
  progress.style.width = amount + '%';
}

window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();

if ('IntersectionObserver' in window) {
  const sectionObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        for (const link of links) {
          const active = link.getAttribute('href') === '#' + entry.target.id;
          link.classList.toggle('current', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        }
      }
    }
  }, { rootMargin: '-20% 0px -62% 0px' });
  for (const section of sections) sectionObserver.observe(section);

  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const revealObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      }
    }, { threshold: 0.07 });
    document.body.classList.add('with-motion');
    document.querySelectorAll('.reveal').forEach((item) => revealObserver.observe(item));
  }
}
