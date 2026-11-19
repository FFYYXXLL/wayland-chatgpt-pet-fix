function usePetSpriteUrl(id, url) {
  const [ready, setReady] = s.useState(() => ({ id, url }));
  const enabled = document.documentElement.hasAttribute("data-umbriel-pet");
  s.useEffect(() => {
    if (!enabled || !url || (ready.id === id && ready.url === url)) return;
    let current = true;
    const next = new Image();
    next.src = url;
    next.decode().then(() => {
      if (current) setReady({ id, url, image: next });
    }).catch(() => {});
    return () => { current = false; };
  }, [enabled, id, url, ready]);
  return enabled && ready.id === id ? ready.url : url;
}
