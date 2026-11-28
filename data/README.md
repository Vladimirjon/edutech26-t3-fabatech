# Datos

**Todos los datos de este repositorio son sintéticos.** No contienen información de estudiantes, familias ni docentes reales.

| Fuente | Qué es | Licencia |
| --- | --- | --- |
| `dataset-ficticio-colegio` de la mesa técnica | Colegio imaginario de 240 estudiantes (8vo EGB a 3ro BGU), año 2025-2026, generado con semilla fija | CC0 |

Si añadimos o modificamos datos (por ejemplo, contactos inventados para el demo), lo anotamos aquí y siguen siendo sintéticos.

Los nombres de las familias se inventaron a partir de los apellidos ficticios del primer hijo. Los tokens de los carnés se generan para el demo. El estudiante técnico `EST-999` y su representante `REP-999` son registros inventados para la prueba de humo.

Para regenerar `supabase/seed.sql` y `data/carnes_demo.pdf`, descomprime el dataset y ejecuta:

```powershell
pip install -r requirements.txt
python scripts/seed.py --dataset "<carpeta del zip>"
```

La lista del demo se obtiene de `estudiantes.csv` del dataset CC0. Los dos primeros estudiantes pertenecen a la misma familia.

| Código | Nombre ficticio | Curso y paralelo | Representante |
| --- | --- | --- | --- |
| EST-006 | Antonella Iturralde Espinoza | 8vo EGB A | REP-006 |
| EST-007 | Sofía Benítez Guerrero | 8vo EGB A | REP-006 |
| EST-001 | Diego Guerrero Delgado | 8vo EGB A | REP-001 |
| EST-002 | Diego Torres Torres | 8vo EGB A | REP-002 |
| EST-003 | Diego Mora Quiroga | 8vo EGB A | REP-003 |
| EST-004 | Emilio Andrade Mora | 8vo EGB A | REP-004 |
| EST-005 | Martín Delgado Cárdenas | 8vo EGB A | REP-005 |
| EST-008 | Sebastián Iturralde Torres | 8vo EGB A | REP-007 |
| EST-009 | Sofía León León | 8vo EGB A | REP-008 |
| EST-010 | Gabriel Benítez Vásconez | 8vo EGB A | REP-009 |
