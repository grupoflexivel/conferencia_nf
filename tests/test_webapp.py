import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


import webapp


app = webapp.app


class WebAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_home_page_contains_progressive_upload_form(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('multipart/form-data', html)
        self.assertRegex(html, r'<img[^>]+src="/logo_topo\.png"')
        self.assertRegex(
            html,
            r'<link[^>]+rel="icon"[^>]+href="/logo_flexivel\.ico"[^>]+type="image/x-icon"',
        )
        self.assertIn('type="radio" name="unidade" value="Matriz"', html)
        self.assertIn('type="radio" name="unidade" value="Filial"', html)
        self.assertIn('name="Matriz__arquivo_sat"', html)
        self.assertIn('name="Filial__arquivo_qive_entrada"', html)
        self.assertIn('.opcao-unidade.selecionada', html)
        self.assertNotIn(':has(input:checked)', html)
        self.assertRegex(html, r'<section[^>]+id="etapa-arquivos"[^>]+hidden')
        self.assertRegex(html, r'<fieldset[^>]+id="uploads-Matriz"[^>]+hidden')
        self.assertRegex(html, r'<fieldset[^>]+id="uploads-Filial"[^>]+hidden')
        self.assertRegex(html, r'<button[^>]+id="processar"[^>]+disabled')
        self.assertIn('function atualizarFormulario', html)

    def test_logo_route_returns_png(self):
        response = self.client.get("/logo_topo.png")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("image/png"))
        response.close()

    def test_favicon_route_returns_ico(self):
        response = self.client.get("/logo_flexivel.ico")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("image/"))
        self.assertEqual(response.data[:4], b"\x00\x00\x01\x00")
        response.close()

    def test_process_requires_unit(self):
        response = self.client.post("/process", data={})

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Selecione uma unidade", response.data)

    def test_process_preserves_selected_unit_field_contract(self):
        def fake_processar_conferencia(_layout, arquivos, caminho_saida):
            Path(caminho_saida).write_bytes(b"technical test output")
            self.assertEqual(set(arquivos), {"arquivo_notas_entrada", "arquivo_sat"})

        with tempfile.TemporaryDirectory() as diretorio_saida:
            with patch.object(webapp, "OUTPUT_DIR", Path(diretorio_saida)):
                with patch.object(webapp, "processar_conferencia", side_effect=fake_processar_conferencia):
                    response = self.client.post(
                        "/process",
                        data={
                            "unidade": "Matriz",
                            "Matriz__arquivo_notas_entrada": (io.BytesIO(b"erp"), "erp.xlsx"),
                            "Matriz__arquivo_sat": (io.BytesIO(b"sat"), "sat.xlsx"),
                            "Filial__arquivo_qive_entrada": (io.BytesIO(b"ignored"), "filial.xlsx"),
                        },
                        content_type="multipart/form-data",
                    )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"technical test output")
        response.close()


if __name__ == "__main__":
    unittest.main()
