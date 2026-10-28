from unittest.mock import patch, Mock
import pytest
import cliente
from cliente import enviar_peticion, con_reintento, consultar_modelo


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    """Reinicia el acumulador de costos antes de cada prueba para evitar contaminación de estado."""
    cliente.costo_total_sesion = 0
    yield


def test_enviar_peticion_credencial_invalida():
    """Confirma que un código 401 lanza ValueError de inmediato sin reintentar."""
    respuesta_falsa = Mock(status_code=401)
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_limite_de_uso():
    """Confirma que un código 429 lanza TimeoutError para dar paso al reintento."""
    respuesta_falsa = Mock(status_code=429)
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})


def test_enviar_peticion_exito():
    """Confirma el camino feliz: código 200 devuelve el diccionario JSON de respuesta."""
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}
    with patch("cliente.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion({"pregunta": "test"})
        assert resultado == {"texto": "respuesta simulada"}


def test_con_reintento_agota_intentos():
    """Confirma que tras agotar los 3 intentos fallidos propaga la excepción original."""
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)


def test_con_reintento_no_reintenta_value_error():
    """Confirma que ValueError corta de inmediato y no llama a time.sleep."""
    def falla_autenticacion():
        raise ValueError("credencial invalida")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(ValueError):
            con_reintento(falla_autenticacion, intentos=3)
        mock_sleep.assert_not_called()


def test_registrar_costo_acumula():
    """Confirma el cálculo exacto de tokens y la suma al costo total de la sesión."""
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = cliente.registrar_costo(respuesta_falsa)
    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_consultar_modelo_convierte_error():
    """Confirma que un TimeoutError agotado se traduce a un RuntimeError amigable para el usuario."""
    error_simulado = TimeoutError("simulado")
    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")