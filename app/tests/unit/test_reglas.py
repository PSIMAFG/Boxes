"""
Tests unitarios para reglas de negocio.
"""
import pytest
from datetime import datetime
from app.dominio.reglas import (
    validar_rut, validar_solapamiento, normalizar_texto,
    esta_en_ventana_tolerancia
)


class TestValidarRUT:
    def test_rut_valido_con_digito(self):
        assert validar_rut("12345678-5") == True

    def test_rut_valido_con_k(self):
        assert validar_rut("7654321-K") == True

    def test_rut_invalido_dv_incorrecto(self):
        assert validar_rut("12345678-9") == False

    def test_rut_formato_invalido(self):
        assert validar_rut("1234567") == False

    def test_rut_con_espacios(self):
        assert validar_rut("  12345678-5  ") == True


class TestValidarSolapamiento:
    def test_no_solape_consecutivos(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 11, 0)
        inicio2 = datetime(2025, 1, 1, 11, 0)
        fin2 = datetime(2025, 1, 1, 12, 0)

        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == False

    def test_solape_parcial(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 11, 30)
        inicio2 = datetime(2025, 1, 1, 11, 0)
        fin2 = datetime(2025, 1, 1, 12, 0)

        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == True

    def test_solape_completo(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 12, 0)
        inicio2 = datetime(2025, 1, 1, 10, 30)
        fin2 = datetime(2025, 1, 1, 11, 30)

        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == True


class TestNormalizarTexto:
    def test_con_acentos(self):
        assert normalizar_texto("José María") == "jose maria"

    def test_con_enies(self):
        assert normalizar_texto("ÑOÑO") == "nono"

    def test_con_espacios_multiples(self):
        assert normalizar_texto("  hola   mundo  ") == "hola mundo"

    def test_mayusculas(self):
        assert normalizar_texto("TEXTO MAYÚSCULAS") == "texto mayusculas"


class TestVentanaTolerancia:
    def test_dentro_de_ventana(self):
        fecha = datetime(2025, 1, 15)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7

        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == True

    def test_fuera_de_ventana(self):
        fecha = datetime(2025, 1, 20)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7

        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == False

    def test_exactamente_en_limite(self):
        fecha = datetime(2025, 1, 17)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7

        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == True
