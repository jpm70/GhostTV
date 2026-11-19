# 👻 GhostTV

Televisión en directo en el navegador: canales de **España y en español**, sin instalar nada.

**▶ En vivo:** https://jpm70.github.io/GhostTV/

Parte del proyecto [Un Fantasma en el Sistema](https://www.unfantasmaenelsistema.com).

## Qué hace
- Reproduce streams HLS con [hls.js](https://github.com/video-dev/hls.js) (Safari usa HLS nativo).
- Buscador, categorías, tema claro/oscuro, volumen y pantalla completa.
- Los canales de España salen primero.

## De dónde salen los canales
Las listas públicas de [iptv-org](https://github.com/iptv-org/iptv) (`countries/es` y `languages/spa`). No se aloja ni retransmite ningún contenido: GhostTV solo enlaza streams que sus emisores ya publican abiertamente.

Muchos streams de esas listas están caídos o no permiten reproducirse desde otra web (CORS), así que la lista se filtra antes de mostrarse:

1. `tools/build_channels.py` descarga las listas, descarta los geobloqueados y comprueba cada canal https (manifiesto HLS válido, primer segmento accesible y cabecera CORS).
2. El resultado se guarda en `channels.json`, que es lo que carga la página.
3. Una GitHub Action (`.github/workflows/refresh-channels.yml`) lo regenera **cada lunes** y hace commit si cambia, de modo que los canales caídos desaparecen y los nuevos aparecen solos.

Si `channels.json` no está disponible, la página recurre a la lista en vivo de iptv-org sin filtrar.

Para regenerarlo a mano:

```bash
python tools/build_channels.py
```

## Limitaciones
- Una comprobación no garantiza el canal: algunos fallan al servir los segmentos de vídeo, y los emisores pueden cortar o geobloquear en cualquier momento.
- Solo se admiten streams https (la página va en https y el navegador bloquea el contenido mixto).

## Desarrollo local
Es HTML estático. Sirve la carpeta con cualquier servidor (con `file://` falla `channels.json`):

```bash
python -m http.server 8000
```

## Aviso
Proyecto educativo y sin ánimo de lucro. Si eres titular de un canal y no quieres que aparezca, pide su retirada en [iptv-org](https://github.com/iptv-org/iptv).
