# Workflows de n8n

Cada workflow exportado desde n8n se guarda aquí como `NN-nombre.json`. Un dueño por workflow.

Antes de versionar un export, elimina `pinData`, incluso si está vacío, y guárdalo en UTF-8 sin BOM. Conserva únicamente referencias a credenciales. Revisa también las cabeceras de HTTP Request, las URL y `staticData`: el validador estructural de credenciales mira los campos `credentials`, y Gitleaks escanea el historial según sus reglas.

Guarda los exports en este directorio. Si agregas `ids.json`, cada nombre debe corresponder a un export presente y cada ID debe ser único en esa instancia.

Valida los exports con `node --test tests/workflows-n8n.test.mjs`.
