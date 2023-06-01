import unittest
import os
from unittest import TestCase

import openai

from custom_nodes.SWAIN.nlp import get_openai_embedding


class TestGetOpenAIEmbedding(unittest.TestCase):
    def setUp(self):
        # Set up api_key
        os.environ["OPENAI_API_KEY"] = "insert_your_api_key_here"

    def test_valid_input(self):
        # Show available models
        models = openai.Model.list()
        print([model.id for model in models['data']])

        # Test valid input
        model = "text-embedding-ada-002"
        text = "Hello, world!"
        embeddings = get_openai_embedding(model, text)
        self.assertIsInstance(embeddings, list)
        self.assertIsInstance(embeddings[0][0], float)

    def test_invalid_model(self):
        # Test invalid model
        model = "text-embedding-dne"
        text = "This shouldn't work"
        try:
            embeddings = get_openai_embedding(model, text)
        except openai.error.InvalidRequestError as e:
            self.assertTrue(True)

    def test_empty_text(self):
        # Test empty text
        model = "text-embedding-ada-002"
        text = ""
        embeddings = get_openai_embedding(model, text)
        self.assertIsInstance(embeddings, list)
        self.assertIsInstance(embeddings[0][0], float)


if __name__ == "__main__":
    unittest.main()


class Test(TestCase):
    def test_oai_completion(self):
        from custom_nodes.SWAIN.nlp import LLMCompletion

        LLMC_obj = LLMCompletion()
        # now test
        result = LLMC_obj.handler("Hello, world!")
        print(result)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)

    def test_llm_completion_prepend(self):
        from custom_nodes.SWAIN.nlp import LLMCompletionPrepend

        LLMCP_obj = LLMCompletionPrepend()
        # now test
        result = LLMCP_obj.handler("Hello, world!", "user", " How are you?")
        print(result)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)

    def test_llm_convo(self):
        from custom_nodes.SWAIN.nlp import LLMConvo

        LLMC_obj = LLMConvo()
        # now test
        result = LLMC_obj.handler("Hello, world!", " How are you?", "user")
        print(result)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['ui'], dict)
        self.assertIsInstance(result['ui']['text'], list)
        self.assertIsInstance(result['ui']['text'][0], list)
        self.assertIsInstance(result['result'], tuple)
        self.assertIsInstance(result['result'][0], list)
        self.assertIsInstance(result['result'][1], list)

    def test_text_concat(self):
        from custom_nodes.SWAIN.nlp import TextConcat

        TC_obj = TextConcat()
        # now test
        result = TC_obj.handler("Hello, world!", "user", " How are you?")
        print(result)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)

    def test_text_concat_new_line(self):
        from custom_nodes.SWAIN.nlp import TextConcatNewLine

        TCNL_obj = TextConcatNewLine()
        # now test
        result = TCNL_obj.handler("Hello, world!", "user", " How are you?")
        print(result)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)


class TestLLMCompletionPrepend(TestCase):
    def test_input_types(self):
        self.fail()

    def test_handler(self):
        self.fail()
