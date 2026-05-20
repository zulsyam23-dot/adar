// Code tabs
document.querySelectorAll('.code-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.code-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('code-' + tab.dataset.tab).classList.add('active');
  });
});

function copyText(btn) {
  const code = btn.parentElement.querySelector('code');
  if (code) {
    navigator.clipboard.writeText(code.textContent).catch(() => {});
    const orig = btn.innerHTML;
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>';
    setTimeout(() => { btn.innerHTML = orig; }, 1500);
  }
}

window.copyText = copyText;
