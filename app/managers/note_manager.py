from datetime import datetime
import bleach

class NoteManager:
    """
    Clase encargada de procesar y validar la lógica de las notas/tareas.
    Separa la lógica de negocio del servicio de persistencia.
    """
    
    # Lista de palabras a censurar (ejemplo de "malsonantes")
    BAD_WORDS = ["mierda", "basura", "tonto", "estúpido"]


    # Usamos @classmethod para acceder a datos de la clase (como cls.BAD_WORDS) y @staticmethod si es una función de apoyo que no necesita ninguna información externa.
    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Limpia el texto eliminando etiquetas HTML y censurando palabras prohibidas.
        
        Args:
            text: El texto original.
        Returns:
            Texto limpio y censurado.
        """
        # 1. Sanitización contra XSS (Abstracción de bleach)
        # Se eliminan todas las etiquetas HTML y atributos para evitar inyección de código malicioso.
        clean_text = bleach.clean(text, tags=[], attributes={}, strip=True)
        
        # 2. Censura de palabras (Lógica de negocio)
        # Se reemplazan las palabras prohibidas por asteriscos.
        for word in cls.BAD_WORDS:
            clean_text = clean_text.replace(word, "*" * len(word))
            clean_text = clean_text.replace(word.capitalize(), "*" * len(word))
            
        return clean_text

    @staticmethod
    def is_expired(deadline: datetime | None) -> bool:
        """
        Comprueba si una nota ha caducado.
        """
        if not deadline:
            return False
        
        # Asegurarse de comparar con timezone si el deadline lo tiene
        now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
        return deadline < now

    @staticmethod
    def validate_deadline(deadline: datetime | None):
        """
        Regla de negocio: El deadline no puede ser una fecha pasada para tareas nuevas.
        """
        if deadline and NoteManager.is_expired(deadline):
            raise ValueError("El deadline no puede ser una fecha pasada")


    @staticmethod
    def get_time_remaining(deadline: datetime | None) -> str:
        """
        Devuelve un mensaje legible con el tiempo restante.
        """
        if not deadline:
            return "Sin fecha límite"
        
        now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
        diff = deadline - now
        
        if diff.days < 0:
            return "Caducada"
        elif diff.days == 0:
            return "Vence hoy"
        else:
            return f"Vence en {diff.days} días"
