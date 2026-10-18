# Feature: email-settings

## Objetivo
Permitir que el usuario configure desde la interfaz el servidor SMTP, el remitente y la plantilla del correo de asignación de guardia, sin editar archivos `.env`.

## Problema
Hoy `SMTPEmailSender` lee `SMTP_*` y `SENDER_EMAIL` del entorno, y el cuerpo/asunto están fijos en `NotifySubstitutionAssignmentHandler`.

## Decisiones
- Configuración guardada en BBDD (tabla `email_settings`, fila única). La contraseña se cifra con Fernet (`cryptography`); la clave vive en `DB_DIR/secret.key`. Protege la contraseña si se copia solo el fichero de BBDD; no protege frente a quien tenga acceso a la carpeta completa.
- Fallback: si no hay configuración en BBDD, se usan las variables de entorno (Docker y desarrollo siguen funcionando).
- La API nunca devuelve la contraseña; solo indica si está configurada. Al guardar sin contraseña se conserva la existente.
- Plantilla con placeholders `{teacher_name}`, `{absent_teacher_name}`, `{group_name}`, `{period}`, `{date}`. Un placeholder desconocido se rechaza al guardar (400).
- Ruta `settings` en el frontend.

## Alcance
- Backend: dominio (`email_settings`), puerto y repositorio, cifrado, `SMTPEmailSender` con configuración dinámica, plantilla en el handler de notificación, endpoints `GET/PUT /api/v1/email/settings` y `POST /api/v1/email/settings/test`.
- Frontend: página de ajustes de correo (servidor, remitente, plantilla, prueba de envío) y enlace en la navegación.
- Fuera de alcance: multi-cuenta, cifrado con DPAPI, plantillas para otros correos.

## Criterios de aceptación
- Guardar la configuración desde la UI y enviar un correo de prueba.
- La contraseña nunca aparece en respuestas ni en logs.
- Un cambio de plantilla afecta al siguiente correo enviado.
- Sin configuración en BBDD, el envío usa `.env`.
- Tests del backend en verde.

## Checks aplicables
- `Backend`: `.venv/Scripts/python.exe -m pytest -q`.
- `Frontend`: `npm run build` (o `ng build`).

## Tareas
- [x] T1 Dominio: `EmailSettings`, plantilla y validación de placeholders (TDD).
- [x] T2 Cifrado de secretos y repositorio SQL de la configuración.
- [x] T3 `SMTPEmailSender` lee la configuración efectiva (BBDD o entorno).
- [x] T4 Notificación usa la plantilla configurada.
- [x] T5 Endpoints de configuración y de prueba.
- [x] T6 Frontend: página de ajustes y enlace de navegación.
- [x] T7 Verificación final (tests, build) y documentación en README.

## Route declaration
- Todas las tareas: ruta inline (edición directa), decisión del agente principal por tamaño acotado y coherencia de contexto.

## Progreso
- Rama `feat/email-settings` creada desde `main`.
- Baseline backend: 46 tests en verde.

## Siguiente paso
T1.
