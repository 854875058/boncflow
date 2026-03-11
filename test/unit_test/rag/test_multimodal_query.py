import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import numpy as np


def _load_multimodal_query_module():
    llm_service_module = types.ModuleType("api.db.services.llm_service")
    llm_service_module.LLMBundle = object

    constants_module = types.ModuleType("common.constants")
    constants_module.LLMType = types.SimpleNamespace(IMAGE2TEXT="image2text")

    multimodal_embedding_module = types.ModuleType("rag.utils.multimodal_embedding")
    multimodal_embedding_module.supports_multimodal_embedding = lambda embedding_model: embedding_model.supports_image_embedding()

    sys.modules["api.db.services.llm_service"] = llm_service_module
    sys.modules["common.constants"] = constants_module
    sys.modules["rag.utils.multimodal_embedding"] = multimodal_embedding_module

    module_path = Path("E:/AI数据集项目/boncflow/rag/utils/multimodal_query.py")
    spec = importlib.util.spec_from_file_location("multimodal_query_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class _EmbeddingWithImage:
    def __init__(self):
        self.query_inputs = []
        self.image_calls = 0

    def supports_image_embedding(self) -> bool:
        return True

    def encode_queries(self, text: str):
        self.query_inputs.append(text)
        return np.asarray([1.0, 0.0], dtype=np.float32), 3

    def encode_image_documents(self, images):
        self.image_calls += 1
        return np.asarray([[0.0, 1.0]], dtype=np.float32), 7


class _EmbeddingTextOnly:
    def __init__(self):
        self.query_inputs = []

    def supports_image_embedding(self) -> bool:
        return False

    def encode_queries(self, text: str):
        self.query_inputs.append(text)
        return np.asarray([0.0, 2.0], dtype=np.float32), 5


def test_prepare_multimodal_query_fuses_text_and_image_vectors_without_summary():
    module = _load_multimodal_query_module()
    model = _EmbeddingWithImage()

    prepared = asyncio.run(
        module.prepare_multimodal_query(
            tenant_id="tenant-1",
            embedding_model=model,
            question="红色挖掘机",
            image_base64="data:image/png;base64,aGVsbG8=",
        )
    )

    np.testing.assert_allclose(prepared.query_vector, [0.4740998, 0.8804711], rtol=1e-5)
    assert prepared.question == "红色挖掘机"
    assert prepared.media_summary == ""
    assert prepared.mode == "image"
    assert model.query_inputs == ["红色挖掘机"]
    assert model.image_calls == 1


def test_prepare_multimodal_query_uses_image_summary_when_embedding_is_text_only():
    module = _load_multimodal_query_module()
    model = _EmbeddingTextOnly()

    class _VisionBundle:
        def __init__(self, tenant_id, llm_type):
            assert tenant_id == "tenant-2"
            assert llm_type == "image2text"

        def describe_with_prompt(self, image, prompt):
            assert isinstance(image, bytes)
            assert "检索图片" in prompt
            return "蓝色卡车停在工地"

    module.LLMBundle = _VisionBundle

    prepared = asyncio.run(
        module.prepare_multimodal_query(
            tenant_id="tenant-2",
            embedding_model=model,
            question="",
            image_base64="data:image/png;base64,aGVsbG8=",
        )
    )

    assert prepared.question == "蓝色卡车停在工地"
    assert prepared.media_summary == "蓝色卡车停在工地"
    assert prepared.mode == "image"
    assert prepared.query_vector == [0.0, 1.0]
    assert model.query_inputs == ["蓝色卡车停在工地"]


def test_prepare_multimodal_query_uses_video_summary_as_query_text():
    module = _load_multimodal_query_module()
    model = _EmbeddingTextOnly()

    class _VisionBundle:
        def __init__(self, tenant_id, llm_type):
            assert tenant_id == "tenant-3"
            assert llm_type == "image2text"

        async def async_chat(self, system, history, gen_conf, video_bytes=None, filename=""):
            assert isinstance(video_bytes, bytes)
            assert filename == "demo.mp4"
            return "视频展示了一辆白色卡车驶入厂区"

    module.LLMBundle = _VisionBundle

    prepared = asyncio.run(
        module.prepare_multimodal_query(
            tenant_id="tenant-3",
            embedding_model=model,
            question="查找相关视频",
            video_base64="data:video/mp4;base64,aGVsbG8=",
            media_filename="demo.mp4",
        )
    )

    assert prepared.question == "查找相关视频\n视频展示了一辆白色卡车驶入厂区"
    assert prepared.media_summary == "视频展示了一辆白色卡车驶入厂区"
    assert prepared.mode == "video"
    assert prepared.query_vector == [0.0, 1.0]
    assert model.query_inputs == ["查找相关视频\n视频展示了一辆白色卡车驶入厂区"]
