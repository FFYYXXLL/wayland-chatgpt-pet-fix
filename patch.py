#!/usr/bin/env python3
"""Build a patched ChatGPT 26.1111.21308 archive from the original."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

CHUNK = ".vite/build/early-bootstrap-226-2f6bd181558008cf.js"
ORIGINAL_HASH = "97adba36c0c0e9e145ab364c82eb3433abe3675ab7c6e3ab282035b67a4d60bb"
RENDERER_NEEDLES = (
    (b'"avatar-overlay-drag-end"', b'beganOnQuickChatBar', b'.setQuickChatStashed(null)'),
    (b'.completeQuickChatFocus(', b'layoutRevision:null'),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def entries(tree, prefix=""):
    for name, entry in tree["files"].items():
        path = prefix + name
        if "files" in entry:
            yield from entries(entry, path + "/")
        elif "offset" in entry:
            yield path, entry


def patch_bundle(data, kind):
    s=data.decode()
    def sub(a,b):
        nonlocal s
        if s.count(a) != 1: raise ValueError("Unexpected bundle signature: " + a)
        s=s.replace(a,b)
    if kind=='main':
        sub('class u1{','const umbrielPet=process.platform==="linux"&&!!process.env.WAYLAND_DISPLAY&&process.env.XDG_CURRENT_DESKTOP?.toLowerCase().split(":").includes("umbriel");class u1{')
        sub('title:eZ.app.getName(),width:uP.width','title:umbrielPet?"Codex Pet Overlay":eZ.app.getName(),width:uP.width')
        sub('initialRoute:"/avatar-overlay"}));','initialRoute:"/avatar-overlay"}));if(umbrielPet){i.on("page-title-updated",ev=>ev.preventDefault());i.setTitle("Codex Pet Overlay");i.setInputShape([])}')
        sub('return P}({display:e,displays:eZ.screen.getAllDisplays()', '''if(umbrielPet){const b=e.workArea,dx=P.windowBounds.x-b.x,dy=P.windowBounds.y-b.y;for(const rect of [P.mascot,P.tray,P.quickChat?.workArea])if(rect){rect.left+=dx;rect.top+=dy}P.windowBounds={...b};P.viewport={width:b.width,height:b.height};P.visibleBounds={left:0,top:0,...P.viewport};P.umbrielOrigin={x:b.x,y:b.y}}return P}({display:e,displays:eZ.screen.getAllDisplays()''')
        sub('function uG(e){return{mascot:', 'function uG(e){return{...(umbrielPet?{umbrielOrigin:e.umbrielOrigin}:{}),mascot:')
        sub('setWindowBounds(e,t,r){if','setWindowBounds(e,t,r){if(umbrielPet){let [w,h]=e.getContentSize();if(w!==t.width||h!==t.height)e.setContentSize(t.width,t.height,false);return}if')
        sub('applyPointerInteractivityPolicy(){let e=this.window;', 'applyPointerInteractivityPolicy(){let e=this.window;if(umbrielPet&&e&&!e.isDestroyed()){e.setInputShape((this.pointerInput.inputShape??[]).map(({left:x,top:y,width,height})=>({x,y,width,height})));return}')
    elif kind == "sprite":
        hook = Path(__file__).with_name("sprite-refresh.js").read_text()
        marker = 'let v=({assetMap:e,className:t,lookFrame:n'
        sub(marker, hook + marker)
        sub('g=(0,s.useRef)(null),v=(0,a.I)(),y=u&&h?', 'g=(0,s.useRef)(null),spriteUrl=usePetSpriteUrl(c.petId??c.assetRef,c.spritesheetUrl??e[c.assetRef]),v=(0,a.I)(),y=u&&h?')
        sub('backgroundImage:`url(${c.spritesheetUrl??e[c.assetRef]})`','backgroundImage:`url(${spriteUrl})`')
    else:
        sub('}(rR.current,ni);l()(rO.current,t)', '}(rR.current,ni);if(umbrielOrigin)umbrielControlRects=a;l()(rO.current,t)')
        sub('r_.setPointerRegions(t,a)','r_.setPointerRegions(umbrielOrigin?[...t,...a.map(({left,top,width,height})=>({left:Math.floor(left),top:Math.floor(top),width:Math.ceil(left+width)-Math.floor(left),height:Math.ceil(top+height)-Math.floor(top)}))]:t,a)')
        sub('function aV(e){', Path(__file__).with_name('hover.js').read_text()+'function aV(e){')
        sub('[nt,na]=(0,g.useState)(!1),','[nt,na]=(0,g.useState)(!1),[overPetControls,setOverPetControls]=(0,g.useState)(false),')
        sub('ns=(0,g.useRef)(0);null!=nr','ns=(0,g.useRef)(0);(0,g.useEffect)(()=>umbrielOrigin?watchPetControlHover(setOverPetControls):undefined,[!!umbrielOrigin]);null!=nr')
        sub('!a4&&(i9||nt||null!=ol)','!a4&&(i9||nt||overPetControls||null!=ol)')
        sub('function aV(e){','let umbrielOrigin=null;function aV(e){')
        sub('return{screenX:e.screenX,screenY:e.screenY,timeMs:', 'return{screenX:umbrielOrigin?e.clientX+umbrielOrigin.x:e.screenX,screenY:umbrielOrigin?e.clientY+umbrielOrigin.y:e.screenY,timeMs:')
        sub('samples:[aV(e)],screenX:e.screenX,screenY:e.screenY','samples:[aV(e)],screenX:aV(e).screenX,screenY:aV(e).screenY')
        sub('pointerScreenX:e.screenX,pointerScreenY:e.screenY,pointerWindowX:', 'pointerScreenX:aV(e).screenX,pointerScreenY:aV(e).screenY,pointerWindowX:')
        sub('eV=e=>{let{isGlobalRealtimeVoicePresentation:', 'eV=e=>{umbrielOrigin=e.layout?.umbrielOrigin??null;document.documentElement.toggleAttribute("data-umbriel-pet",!!umbrielOrigin);let{isGlobalRealtimeVoicePresentation:')
        sub('"data-avatar-overlay-hit-region":"tray-mascot-bridge"', '"data-avatar-overlay-hit-region":umbrielOrigin?undefined:"tray-mascot-bridge"')
    with tempfile.TemporaryDirectory() as directory:
        script = Path(directory) / ("main.cjs" if kind == "main" else "renderer.mjs")
        script.write_text(s)
        subprocess.run(["node", "--check", str(script)], check=True)
    return s.encode()


def build(source_path, output_path):
    if source_path.resolve() == output_path.resolve():
        raise SystemExit("Choose a separate output file.")
    with source_path.open("rb") as source:
        _, header_size, _, json_size = struct.unpack("<IIII", source.read(16))
        header = json.loads(source.read(json_size))
        old_data_start = 8 + header_size
        archive_entries = sorted(entries(header), key=lambda item: int(item[1]["offset"]))
        replacements = []
        shift = 0
        kinds = []
        for path, entry in archive_entries:
            offset, old_size = int(entry["offset"]), entry["size"]
            entry["offset"] = str(offset + shift)
            if not path.endswith(".js"):
                continue
            source.seek(old_data_start + offset)
            data = source.read(old_size)
            if path.startswith(".vite/build/") and b'applyPointerInteractivityPolicy(){' in data and b'initialRoute:"/avatar-overlay"' in data:
                kind = "main"
            elif b'let v=({assetMap:e,className:t,lookFrame:n' in data and b'backgroundImage:`url(${c.spritesheetUrl??e[c.assetRef]})`' in data:
                kind = "sprite"
            elif any(all(needle in data for needle in group) for group in RENDERER_NEEDLES):
                kind = "renderer"

            else:
                continue
            kinds.append(kind)
            patched = patch_bundle(data, kind)
            print(f"Patched {kind} {path}")
            entry["size"] = len(patched)
            integrity = entry["integrity"]
            block_size = integrity["blockSize"]
            integrity["hash"] = digest(patched)
            integrity["blocks"] = [
                digest(patched[i:i + block_size]) for i in range(0, len(patched), block_size)
            ]
            replacements.append((offset, old_size, patched))
            shift += len(patched) - old_size
        if sorted(kinds) != ["main", "renderer", "sprite"]:
            raise SystemExit("Expected the main, overlay renderer and sprite bundles.")

        serialized = json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        padding = b"\0" * (-len(serialized) % 4)
        payload = len(serialized) + len(padding) + 4
        with output_path.open("xb") as output:
            output.write(struct.pack("<IIII", 4, payload + 4, payload, len(serialized)))
            output.write(serialized)
            output.write(padding)
            source.seek(old_data_start)
            for offset, old_size, patched in replacements:
                remaining = old_data_start + offset - source.tell()
                while remaining:
                    block = source.read(min(remaining, 1024 * 1024))
                    if not block:
                        raise EOFError("Truncated input archive")
                    output.write(block)
                    remaining -= len(block)
                output.write(patched)
                source.seek(old_data_start + offset + old_size, os.SEEK_SET)
            shutil.copyfileobj(source, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.original, args.output)
