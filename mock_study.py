import unittest
from unittest.mock import Mock


class MyObject:
    def __init__(self):
        self.attribute = 'original value'


class MyTestCase(unittest.TestCase):
    def test_mock_attribute(self):
        # Crie uma instância do objeto que deseja testar
        obj = MyObject()

        # Verifique o valor original do atributo
        self.assertEqual(obj.attribute, 'original value')

        # Crie um mock para o atributo
        obj.attribute = Mock()
        obj.attribute.return_value = 'mocked value'

        # Agora o atributo retornará o valor mockado
        self.assertEqual(obj.attribute(), 'mocked value')

        # Verifique se o mock foi chamado
        obj.attribute.assert_called_once()


if __name__ == '__main__':
    unittest.main()
