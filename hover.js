let umbrielControlRects = [];
function watchPetControlHover(setHovered) {
  const selector = '[data-avatar-overlay-native-glass-group="pet-controls"],[data-avatar-overlay-hit-region="mascot"]';
  let timer;
  function update(target, event) {
    const inside = event && umbrielControlRects.some(r => event.clientX >= r.left && event.clientX < r.left + r.width && event.clientY >= r.top && event.clientY < r.top + r.height);
    if (inside || (target instanceof Element && target.closest(selector))) {
      clearTimeout(timer);
      timer = undefined;
      setHovered(true);
    } else if (timer === undefined) {
      timer = setTimeout(() => {
        timer = undefined;
        setHovered(false);
      }, 180);
    }
  }
  const enter = event => update(event.target, event);
  const leave = event => update(event.relatedTarget, event.relatedTarget ? event : null);
  document.addEventListener('pointermove', enter, true);
  document.addEventListener('pointerover', enter, true);
  document.addEventListener('pointerout', leave, true);
  return () => {
    clearTimeout(timer);
    document.removeEventListener('pointermove', enter, true);
    document.removeEventListener('pointerover', enter, true);
    document.removeEventListener('pointerout', leave, true);
  };
}
