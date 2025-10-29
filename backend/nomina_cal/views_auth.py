from utils.email_api import enviar_correo_api

enviar_correo_api(
    "🔐 Recuperación de contraseña",
    f"Hola {usuario.nombre}, hacé clic aquí para restablecer tu contraseña: {reset_link}",
    [usuario.email]
)
